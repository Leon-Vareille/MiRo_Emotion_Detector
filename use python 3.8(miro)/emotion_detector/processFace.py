#!/usr/bin/env python

"""
A python program to run the face detection media pipe model on the image sent from bothEyes

Subscribes to:
    /bothEyes

publishes to:
    /miro/control/kinematic_joints
    
Service:
    imgService
"""



import rospy
from emotion_detector.srv import returnFrame, returnFrameResponse
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image
from sensor_msgs.msg import JointState

import sys
import os
sys.path.append("/opt/miro/configs/LeonMiroCode/Libraries")
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import matplotlib.pyplot as plt

from cv_bridge import CvBridge
import cv2
import numpy as np

frameToProcess = None
frameToSend = None

height = 0
width = 0

noFaceCounter = 0
neck = [-0.10471975803375244, 0.5, 0.0, 0.31]
JointValue = 0.0
facePosition = None

def saveNeck(data):
    global neck
    neck = list(data.position)



def saveImg(frame):
    global frameToProcess
    global height, width
    br = CvBridge()
    frame = br.compressed_imgmsg_to_cv2(frame)
    frameToProcess = frame
    height, width = frame.shape[:2]
    #print("Saved image yippee")
    



def processFrame(value):
    global frameToSend
    global frameToProcess
    global height, width
    global facePosition
    

    print("Recieved request")

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

                #Parse the numpy frame array
                frameArray =np.array(frameToProcess.data)
               
                frameArray = frameArray[int(highY/1.1):lowY, leftX:rightX]

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
    processFrame(0)

    print("Sending response...")
    br = CvBridge()

    try:
        frameToSend = cv2.cvtColor(frameToSend, cv2.COLOR_BGR2GRAY)
    except:
        print(frameToSend.shape)

    cv2.imwrite("eyeImages/faceBox.jpg", frameToSend)
    actualImg = br.cv2_to_imgmsg(frameToSend)

    height, width=frameToSend.shape

    return actualImg.data, height, width
















def correctNeck(value):
    global facePosition
    global neck
    global noFaceCounter

    neckPos = [-0.10471975803375244, 0.5, 0.0, 0.31]

    processFrame(0)
    print("NoFaceCounter: ",noFaceCounter)
    if isinstance(facePosition, type(None)):
        noFaceCounter +=1

        if noFaceCounter>20:
            pub = rospy.Publisher('/miro/control/kinematic_joints', JointState, queue_size=1)
            pub.publish(JointState().header, JointState().name, neckPos ,JointState().velocity, JointState().effort)
            noFaceCounter = 0
        return

    print("facePosition: ", facePosition)




    if not (facePosition[0] < 0.4 or facePosition[0]>0.6 or facePosition[1] < 0.6 or facePosition[1]>0.8):
        #We have been found to be in a good enough place. Dont move
        return


    
    #"""This is for the horizontal joints.
    #Loops for each set position for the horizontal joint
    positionPeriod = 0.058
    whereWeAre=neck[2]
    #JointOffset = 1.6
    
    for i in range(0,17):
        
        print("Is ", (i*positionPeriod - (positionPeriod/2)) , " < ", facePosition[0] , " < ", (i*positionPeriod + (positionPeriod/2)))
        #if facePosition is greater than the lower limit and lesser than the upper limit
        if (facePosition[0] > (i*positionPeriod - positionPeriod/2))and(facePosition[0] < (i*positionPeriod + positionPeriod/2)):
            #If this is true, we have found which horizontal joint position the face is closest to, we can leave the loop
            JointOffset = 1.6-(i*0.2)
            print("We need to move by: " , JointOffset)
            break
        

    #Outside the loop we can apply the found joint value
    print("The joint value currently is(Horizontal): ", whereWeAre)
    JointValue = whereWeAre + JointOffset

    #Stops the robot from trying to go to exceptional joint values
    if JointValue < -1.6:
        JointValue = -1.6

    elif JointValue > 1.6:
        JointValue = 1.6

    neckPos[2] = JointValue
    print("Setting (Horizontal) joint to ... ", JointValue)
    #""" #end horizontal joints


    

    #"""Now for the vertival joints

    positionPeriod = 0.166
    whereWeAre=neck[3]

    for i in range(0,7):

        if (facePosition[1] > (i*positionPeriod - (positionPeriod/2)))and(facePosition[1] < (i*positionPeriod + (positionPeriod/2))):
            #We have the line for the the vertical joints to move to

            JointOffset = (-0.39)+(i*0.11)
            print("We need to move by: " , JointOffset)
            break

    
    #Outside the loop we can apply the found joint value
    print("The joint value currently is (Vertical): ", whereWeAre)
    JointValue = whereWeAre + JointOffset

    #Stops the robot from trying to go to exceptional joint values
    if JointValue < -0.39:
        JointValue = 0.39

    elif JointValue > 0.28:
        JointValue = 0.28

    neckPos[3] = JointValue
    print("Setting (Vertical) joint to ... ", JointValue)
    #""" #end vertical joints





    pub = rospy.Publisher('/miro/control/kinematic_joints', JointState, queue_size=1)
    pub.publish(JointState().header, JointState().name, neckPos ,JointState().velocity, JointState().effort)
    
    









if __name__ == "__main__":
    try:
        rospy.init_node('processFace')
       

        try:
            print("Node Initilised!")

            
            
            rospy.Subscriber('bothEyes', CompressedImage, saveImg)
            rospy.Subscriber('miro/sensors/kinematic_joints', JointState, saveNeck)
            
            rospy.Timer(rospy.Duration(1,0), correctNeck)

            s = rospy.Service("ImgService", returnFrame, sendFrame)
            rospy.spin()
            
        except KeyboardInterrupt():
            pass
    
    except rospy.ROSInternalException:
        pass