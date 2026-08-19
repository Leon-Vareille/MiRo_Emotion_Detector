#!/usr/bin/env python

"""
A python program that will prevent the stop start of the distToWheels and precessFace nodes.
It will take the outputs of thoes files and just constantly publish them untill a new message is recieved

Subscribes to:
    /wheelMovement
    


publishes to:
    /miro/control/cosmetic_joints
"""


import rospy
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TwistStamped

wheelMovement = TwistStamped()
currentNeck = None
stepNum = 1





def pubWheel(data):
    global wheelMovement

    if isinstance(wheelMovement, type(None)):
        return

    pub = rospy.Publisher("miro/control/cmd_vel", TwistStamped, queue_size=1)
    pub.publish(wheelMovement)


def getWheel(data):
    global wheelMovement
    wheelMovement = data


if __name__ == "__main__":
    try:
        rospy.init_node('jitterless')
        print("jitterless Node Initilised!")
       
        try:
            
            rospy.Subscriber('/wheelMovement',TwistStamped, getWheel)
            

            rospy.Timer(rospy.Duration(nsecs=125000000), pubWheel) #8 times a sec
        
            rospy.spin()
            
        except KeyboardInterrupt():
            pass
    
    except rospy.ROSInternalException:
        pass