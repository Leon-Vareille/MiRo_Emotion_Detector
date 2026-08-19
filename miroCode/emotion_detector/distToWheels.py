#!/usr/bin/env python

"""
A python program that will take an image and run a model to figure out distance and position,
 then decides and publish how the wheels will move


subscribes to /bothEyes

publishes to /wheelMovement
"""



import rospy
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import Range

import sys
sys.path.append("/opt/miro/configs/LeonMiroCode/Libraries")
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import matplotlib.pyplot as plt

import compressed_image_transport
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2
import numpy as np


#global varibles
dist = 0.0
pos = 0.0
personPresent = False
getPos = True

def updateLR(data):
    global getPos
    if not getPos:
        return

    global pos, personPresent
    getPos = False


    #Getting the array frame from the Image type
    
    frame = br.compressed_imgmsg_to_cv2(data)
    #frame = br.imgmsg_to_cv2(data)
    height, width= frame.shape[:2]


    #Pose detection
    mp_pose_detection = mp.solutions.pose

    pose = mp_pose_detection.Pose(
        static_image_mode=False, 
        min_detection_confidence=0.15
    )
    results = pose.process(frame)

    if results == None:
        print("WE GOT NOTHIN")
   

    #Check if a person is even present
    if not results.pose_landmarks:
        personPresent = False
        print("Nobody is there")
        pose.close()
        return
    

    #A person is present
    personPresent = True
    print("We see someone")
    for kpCounter, kp in enumerate(results.pose_landmarks.landmark):
        #print("Doing key point: ", kpCounter)
        #get the co ordinates of each KP
        x = int(kp.x * width)
        y = int(kp.y * height)

        if kpCounter == 11:
            leftShoulder = (x, y)
        elif kpCounter == 12:
            rightShoulder = (x, y)


        #Put said co-ords on the frame
        cv2.circle(frame,(x,y), 2, (0,255,0),4)
    
    #"""save the image
    cv2.imwrite("eyeImages/PoseImg.jpg", frame)
    
    #"""

    #get the mid point of the shoulders
    midpoint = ((leftShoulder[0]+rightShoulder[0])/2,(leftShoulder[1]+rightShoulder[1])/2)
    print(midpoint)



    pose.close()
    pos = midpoint[0]
    




def updateDist(data):
    global dist
    dist = data.range
    #print("Distance: " , dist , "    Type: ", type(dist))



def applyMovement():
    global dist, pos
    global personPresent

    msg = TwistStamped()
    pub = rospy.Publisher("/wheelMovement", TwistStamped, queue_size=1)

    reps = 1
    print(pos)

    if not personPresent:
        msg.twist.angular.z=0
    elif pos > 490:

        msg.twist.angular.z=-0.25
        
        

    elif pos<410:

        msg.twist.angular.z=0.25

    else:
        msg.twist.angular.z=0
    
        if dist > 0.5:
            msg.twist.linear.x=3
            print("We go forwards")

        elif dist < 0.1:
            msg.twist.linear.x=-3
        
        
    pub.publish(msg.header, msg.twist)
    




def allowGetPos(value):
    global getPos
    getPos = True
    applyMovement()
        
        




if __name__ == "__main__":
    try:
        rospy.init_node('distToWheels') 
        br = CvBridge()
        
        

        try:

            #Code go here
            rospy.Subscriber('bothEyes', CompressedImage, updateLR)
            rospy.Subscriber('/miro/sensors/sonar', Range, updateDist)

            rospy.Timer(rospy.Duration(0,800000000), allowGetPos)
            #rospy.Timer(rospy.Duration(0,900000000), applyMovement)
        
            

            
                
            rospy.spin()
        
        except KeyboardInterrupt():
                pass
    except rospy.ROSInternalException:
        pass