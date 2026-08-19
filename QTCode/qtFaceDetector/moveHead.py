#!/usr/bin/env python

"""
A python program that gets the face pos and then moves the head to look at the head

subscribes to:
    -/facePosition


publishes to
    -/qt_robot/head_position/command
"""

import rospy

from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from qt_robot_interface.srv import speech_say



facePosition = None
whereWeAre = [0,0]
headTimer = 0
allowTimeout = False

def getWhereWeAre(data):
    global whereWeAre
    whereWeAre = data.position[:2]


def getfacePosition(data):
    global facePosition
    global headTimer
    facePosition = data.data
    headTimer = 0


def headTimeout(data):
    global headTimer, allowTimeout
    if allowTimeout:
        headTimer += 1


def setNeck(data):
    global facePosition
    global whereWeAre
    global headTimer, allowTimeout


    if isinstance(facePosition, type(None)):
        return

    if headTimer >= 5:
        #If it has been 5 seconds without seeing someone, go back to default
        headTimer = 0
        allowTimeout = False
        JointValue =[0,0]

        pub = rospy.Publisher('/qt_robot/head_position/command', Float64MultiArray, queue_size=1)
        pub.publish(Float64MultiArray().layout, JointValue)

        say = rospy.ServiceProxy("/qt_robot/speech/say", speech_say)
        say("Where did you go")
        return
    

    allowTimeout = True
    basePos = [0,0]
    JointValue = [0,0]
    JointOffset = 0

    #Horizontal Joints
    JointUpper = 60
    JointLower = -60
    
    positions = 55
    positionPeriod = 1/positions
    JointPeriod = (JointUpper-JointLower)/positions

    
    if (not (facePosition[0] < 0.35 or facePosition[0]>0.65 or facePosition[1] < 0.35 or facePosition[1]>0.65)):
        #We have been found to be in a good enough place. Dont move
        return



    for i in range(0,positions):


        print("is ",(i*positionPeriod - (positionPeriod/2)) , " < ",facePosition[0], " < ", (i*positionPeriod + (positionPeriod/2)))
        if (facePosition[0] > (i*positionPeriod - (positionPeriod/2)))and(facePosition[0] < (i*positionPeriod + (positionPeriod/2))):
            #We have the line for the the horizontal joints to move to

            JointOffset = (JointLower)+(i*JointPeriod)
            print("We need to move by: " , JointOffset)
            break


    
    #Outside the loop we can apply the found joint value
    print("The joint value currently is (horizontal): ", whereWeAre)
    JointValue[0] = whereWeAre[1] - JointOffset

    #Stops the robot from trying to go to exceptional joint values
    if JointValue[0] < -60:
        JointValue[0] = -60

    elif JointValue[0] > 60:
        JointValue[0] = 60

    print("Setting (horizontal) joint to ... ", JointValue[0])




    #"""vertical Joints
    JointUpper = 25
    JointLower = -25
    
    positions = 10
    positionPeriod = 1/positions
    JointPeriod = (JointUpper-JointLower)/positions

    for i in range(0,positions):


        print("is ",(i*positionPeriod - (positionPeriod/2)) , " < ",facePosition[1], " < ", (i*positionPeriod + (positionPeriod/2)))
        if (facePosition[1] > (i*positionPeriod - (positionPeriod/2)))and(facePosition[1] < (i*positionPeriod + (positionPeriod/2))):
            #We have the line for the the horizontal joints to move to

            JointOffset = (JointLower)+(i*JointPeriod)
            print("We need to move by: " , JointOffset)
            break



    
    #Outside the loop we can apply the found joint value
    print("The joint value currently is (Vertical): ", whereWeAre)
    JointValue[1] = whereWeAre[0] + JointOffset

    #Stops the robot from trying to go to exceptional joint values
    if JointValue[1] < -25:
        JointValue[1] = -25

    elif JointValue[1] > 25:
        JointValue[1] = 25

    print("Setting (vertical) joint to ... ", JointValue[1])
    #"""


    #now we need to publish to head
    pub = rospy.Publisher('/qt_robot/head_position/command', Float64MultiArray, queue_size=1)

    pub.publish(Float64MultiArray().layout, JointValue)







if __name__ == '__main__':
    rospy.init_node('moveHead')
    print("Node moveHead Initilised")

    # gets the face position
    rospy.Subscriber('/facePosition', Float64MultiArray, getfacePosition)

    #gets the curent head position
    rospy.Subscriber('/qt_robot/joints/state', JointState, getWhereWeAre)

    #gets the joint values
    rospy.Timer(rospy.Duration(nsecs=500000000), setNeck)

    rospy.Timer(rospy.Duration(secs=1), headTimeout)

   
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass
