#!/usr/bin/env python

"""
A python program to save the kinematic and cosmetic joint values to a text file

Subscribes to:
    /miro/control/cosmetic_joints
    /miro/control/kinematic_joints
    /miro/control/cmd_vel

publishes to:

writes to:
    logs/kinematic/year - month - day.txt
    logs/cosmetic/year - month - day.txt

"""


import rospy
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TwistStamped

import datetime

writable = [1,1,1]


def write(data, dataType):
    global writable

    #Checks if we can write for the specific joint 
    if dataType == "kinematic" and writable[0]:
        writable[0] = 0

    elif dataType == "cosmetic" and writable[1]:
        writable[1] = 0
        
    elif dataType == "cmd_vel" and writable[2]:
        writable[2] = 0
        
    else:
        return
    

    print(dataType)

    #gets the date and time
    time = datetime.datetime.now()

    #gets the file path
    filePath = str(time.year) +"-"+ str(time.month) +"-"+ str(time.day)+".txt"
    filePath = "/opt/miro/configs/LeonMiroCode/ws/logs/"+dataType+"/"+filePath+".txt"


    #creates and writes to the file
    f = open(filePath, "a")

    #labels the joints with the time 
    f.write(str(time.hour)+" - " + str(time.minute) +" - " + str(time.second)+"\n")
    f.write(str(data))
    f.write("\n\n\n")
    f.close()

def allowWrite(data):
    global writable
    writable = [1,1,1]


if __name__ == "__main__":
    try:
        rospy.init_node('saveJointValues')
        print("saveJointValues Node Initilised!")
       
        try:
            #Allows the joints to be written to every second, reduce nsecs to have it happen more often
            rospy.Timer(rospy.Duration(nsecs=1000000000), allowWrite)

            """
            This only works for the control, and thus whenever the joint values get published
            Kinematic joints has a sensor topic whihc could be used instead, but cosmetic joints has no such topic
            """
            rospy.Subscriber('miro/control/cosmetic_joints', Float32MultiArray, write, callback_args="cosmetic" )
            rospy.Subscriber('miro/control/kinematic_joints', JointState, write, callback_args="kinematic")
            rospy.Subscriber('miro/control/cmd_vel',TwistStamped, write,callback_args="cmd_vel")
        
            rospy.spin()
            
        except KeyboardInterrupt():
            pass
    
    except rospy.ROSInternalException:
        pass