#!/usr/bin/env python

"""
A python program to retrieve the face seen by the qt camera, process it, then send it over the websocket via a service

publishes:
    -/facePosition

service:
    -imgSevice


subscribes to
    -/camera/color/image_raw

"""

import rospy

from std_msgs.msg import String
from qtFaceDetector.srv import returnFrame, returnFrameResponse
from sensor_msgs.msg import Image
from qt_robot_interface.srv import *
from std_msgs.msg import Float64MultiArray

sys.path.append("/opt/ros/qt_ws/configs/LeonCode/Libraries")
import mediapipe as mp

from cv_bridge import CvBridge
import cv2
import numpy as np


frameToProcess = None
height = 0
width = 0
frameToSend = None

def saveImage(data):
    print("Im saveImage")
    global frameToProcess
    global height, width
    br = CvBridge()
    frameToProcess = br.imgmsg_to_cv2(data)
    height, width = frameToProcess.shape[:2]

def processFace(data):
    global frameToProcess
    global frameToSend


    if isinstance(frameToProcess, type(None)):
        return

    
    mp_face_detection = mp.solutions.face_detection

    face_detection = mp_face_detection.FaceDetection(
    model_selection=1, 
    min_detection_confidence=0.75
    )
    
    
    results = face_detection.process(frameToProcess)

    print(results)

    KEYPOINT_LABELS = {
    0: "Right Eye",
    1: "Left Eye",
    2: "Nose Tip",
    3: "Mouth Centre",
    4: "Right Ear",
    5: "Left Ear"
    }


    if results.detections:
        for face_idx, detection in enumerate(results.detections):
            print(f"\n--- Face #{face_idx} Keypoints ---")
            
            # Check if the model successfully returned keypoints
            if detection.location_data.relative_keypoints:
                faceBox = detection.location_data.relative_bounding_box
                

                print("Face box co ordiantes")
                leftX = int(faceBox.xmin * width)
                highY = int(faceBox.ymin * height)
                rightX = int((faceBox.xmin + faceBox.width)*width)
                lowY = int((faceBox.ymin + faceBox.height)*height)
                print(leftX, highY, rightX, lowY)

                #Get the mid point of the face box as the mp of face
                facePosition = [faceBox.xmin + (faceBox.width/2),faceBox.ymin + (faceBox.height/2)]


                #Here we are going to send position data to getPos.

                pub = rospy.Publisher('/facePosition',Float64MultiArray,queue_size=1)
                pub.publish(Float64MultiArray().layout,facePosition)
               
                






                #Parse the numpy frame array
                frameArray =np.array(frameToProcess.data)
               
                frameArray = frameArray[int((highY/1.1)*0.9):int(lowY*1.1), int(leftX*0.9):int(rightX*1.1)]

                try:
                    face_detection.close()
                except:
                    #face detection is of noneType
                    pass
    else:
        face_detection.close()
        facePosition = None
        return

    
    frameToSend = frameArray


def sendFrame(value):
    global frameToSend
    processFace(0)

    if isinstance(frameToSend, type(None)):
        return

    print("Sending response...")
    br = CvBridge()

    try:
        #frameToSend = cv2.cvtColor(frameToSend, cv2.COLOR_BGR2GRAY)
        pass
    except:
        print(frameToSend.shape)

    cv2.imwrite("eyeImages/faceBox.jpg", frameToSend)
    actualImg = br.cv2_to_imgmsg(frameToSend)

    height, width=frameToSend.shape[:2]
    cv2.imwrite("images/faxeBox.jpg", frameToSend)
    return actualImg.data, height, width





if __name__ == '__main__':
    rospy.init_node('getFace')
    print("Node getFace Initilised")    

    # get the image
    rospy.Subscriber('/camera/color/image_raw', Image, saveImage)

    #process to get just the face
    rospy.Timer(rospy.Duration(nsecs=100000000), processFace)

    #service to send frame to lerobot model
    s = rospy.Service("ImgService", returnFrame, sendFrame)

    
   
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass

