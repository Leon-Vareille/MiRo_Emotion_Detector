#!/usr/bin/env python

"""
This camera is ont attached to the head of the QTrobot, the way the head moving works relies on the moventent of the camera due to the movement of the head
Because of this, while using this node along with moveHead.yp, the head will only ever move completly left or right based on the faces position to the camera

This could be remidied with a slightly differnet method of moving the head, one that does rely on the previous location of the head like how we ahve it now, 
it would be a more direct mapping on face location to joint value as opposed to face location to joint change/offset.

"""

import rospy

from zed_interfaces.msg import ObjectsStamped
from std_msgs.msg import Float64MultiArray

mp = None

def saveFace(data):
    global mp
    x1 =  data.objects[0].bounding_box_2d.corners[0].kp[0]
    x2 = data.objects[0].bounding_box_2d.corners[2].kp[0]
    y1 = data.objects[0].bounding_box_2d.corners[0].kp[1]
    y2 = data.objects[0].bounding_box_2d.corners[2].kp[1]

    mp = ((x1+x2)/2, (y1+y2)/2)

    #I use the position as a percentage
    mp =(mp[0]/1280, mp[1]/720)
    print(mp)

   
    
def pubMP(data):
    global mp

    pub = rospy.Publisher("/facePositionZ", Float64MultiArray, queue_size=1)
    pub.publish(Float64MultiArray().layout,mp)


if __name__ == '__main__':
    rospy.init_node('zedi2GetFace')
    print("Node zedi2GetFace Initilised")

   

    rospy.Subscriber('/zed2i/zed_node/obj_det/objects', ObjectsStamped, saveFace)

    rospy.Timer(rospy.Duration(nsecs=500000000), pubMP)
    

   
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass

