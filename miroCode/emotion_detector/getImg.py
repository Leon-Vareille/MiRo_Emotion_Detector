#!/usr/bin/env python

"""
A python program to get the images from the two eyes and combine them into one image

Subscribes to:
    /Miro/sensors/caml
    /Miro/sensors/camr

publishes to:
    /bothEyes
"""



import rospy

import compressed_image_transport
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2
import numpy as np



frame = None
leftEye = None
rightEye = None

timeBefore = "right"





def callback(data,eye):
    global timeBefore
    global frame
    global leftEye, rightEye

    if timeBefore == eye:
        return
  

    br = CvBridge()
    frame = br.compressed_imgmsg_to_cv2(data)
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    

    #used to differnciate the left eye img and the right
    if eye == "left":
        print("left")
     
        cv2.imwrite("eyeImages/leftEye.jpg",frame)
        leftEye =frame

    #""" code for using both eyes
    else:
        print("Right")
        height, width,rgb =frame.shape

        #cropping part of the img
        frame = frame[:,int(width*0.58):width,:]

        #rotate the img
        height, width,rgb =frame.shape
        center = (width/2, height/2)
        rotation_matrix = cv2.getRotationMatrix2D(center, -28, 1)

        frame = cv2.warpAffine(frame, rotation_matrix, (width, height))
        
        print(frame.shape)


        cv2.imwrite("eyeImages/rightEye.jpg",frame)
        rightEye =frame

    


    try:
        h1, w1 = leftEye.shape[:2]
    except:
        leftEye = np.zeros((360, 640, 3), np.uint8)
        h1, w1 = leftEye.shape[:2]
        

    try:
        h2, w2 = rightEye.shape[:2]
    except:
        rightEye = np.zeros((360, 640, 3), np.uint8)
        h2, w2 = rightEye.shape[:2]

    #create empty matrix
    entireFrame = np.zeros((max(h1, h2), w1+w2,3), np.uint8)

    #combine 2 images
    entireFrame[:h1, :w1,:3] = leftEye
    entireFrame[:h2, w1:w1+w2,:3] = rightEye
  

    cv2.imwrite("eyeImages/BothEyes.jpg", entireFrame)
    actualFrame=entireFrame

    timeBefore = eye
    #""" end code for both eyes

    
    """ only use left eye code 
    actualFrame = leftEye
    #"""

    pub = rospy.Publisher("bothEyes", CompressedImage, queue_size=1)
    img = br.cv2_to_compressed_imgmsg(actualFrame)
    pub.publish(img)





if __name__ == "__main__":
    try:
        rospy.init_node('getImage')
       

        try:
            print("Node Initilised!")
            
            rospy.Subscriber('/miro/sensors/caml/compressed', CompressedImage, callback, callback_args="left")
            rospy.Subscriber('/miro/sensors/camr/compressed', CompressedImage, callback, callback_args="right")
            
            rospy.spin()
            
        except KeyboardInterrupt():
            pass
    
    except rospy.ROSInternalException:
        pass