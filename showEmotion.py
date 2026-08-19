#!/usr/bin/env python

"""
A python program to retrieve an emotion from /emotion topic, then display said emotion ontp the QT robot

subscribes to:
    -emotion
    

services:
    -/qt_robot/emotion/show
"""

import rospy

from qt_gesture_controller.srv import gesture_play
from qt_robot_interface.srv import *
from std_msgs.msg import Int8
from std_msgs.msg import String

emotion = None
allowEmotionToRobot = False

def allowEmotion(data):
    global allowEmotionToRobot
    allowEmotionToRobot = True


def getEmotion(data):
    global emotion
    emotion = data.data
    
def emotionToRobot(data):
    global emotion, allowEmotionToRobot
    
    #emotion = 3
    print("Passing through: ", emotion)

    if emotion == None or not(allowEmotionToRobot):
        #This shouldnt ever happen, as the subscriber should trigger before the timer does
        print("Returning...")
        return
    

     
    

    """For the other ones
    if emotion == 0:#Angry
        emotionShow("QT/angry")
        print("angry")
        
    elif emotion == 1:#Disgusted
        emotionShow("QT/disgusted")
        print("disgusted")
        
    elif emotion == 2:#afraid
        emotionShow("QT/afraid")
        print("afraid")
        
    elif emotion == 3:#Happy
        emotionShow("QT/happy")
        print("happy")

    elif emotion == 4:#Sad
        emotionShow("QT/sad")
        print("sad")

    elif emotion == 5:#Surprised
        #There is no surprised emotion in QT 
        emotionShow("QT/neutral state blinking")
        print("Surprised")
        
    elif emotion == 6:#Neutral
        emotionShow("QT/neutral state blinking")
        print("default 6")
        
    else:#Defualt
        emotionShow("QT/neutral state blinking")
        print("default else")
    #"""

    #"""For the carlosleao lerobot model
    allowEmotionToRobot = False
    if emotion == 0:#Neutral
        emotionShow.publish("QT/neutral state blinking")
        allowEmotionToRobot = True
        print("default 0")

        
    elif emotion == 1:#Happy
        emotionShow.publish("QT/happy")
        playGesture.publish("QT/happy")
        print("happy")

    elif emotion == 2:#Surprised
        #There is no surprised emotion in QT 
        emotionShow.publish("QT/breathing exercise")
        playGesture.publish("QT/surprised")
        print("Surprised")
        
    elif emotion == 3:#Sad
        emotionShow.publish("QT/sad")
        playGesture.publish("QT/sad")
        print("sad")

    elif emotion == 4:#Angry
        emotionShow.publish("QT/angry")
        playGesture.publish("QT/angry")
        print("angry")
        
    elif emotion == 5:#Disgusted Cant see this one very good
        #No gesture for this one
        emotionShow.publish("QT/disgusted")
        print("disgusted")
        
    elif emotion == 6:#afraid
        #No gesture for this one
        emotionShow.publish("QT/afraid")
        print("afraid")
        
    else:#Defualt
        emotionShow.publish("QT/neutral state blinking")
        print("default else")
    #"""







if __name__ == '__main__':
    rospy.init_node('showEmotion')
    print("Node showEmotion Initilised")

    #Run the subscriber to get the emotion
    rospy.Subscriber("/emotion", Int8, getEmotion)



    #sets up the publishers to show the emotion 
    emotionShow = rospy.Publisher('qt_robot/emotion/show', String, queue_size=1)
    playGesture = rospy.Publisher('qt_robot/gesture/play', String, queue_size=1)

    #timer to show the emotion saved, any lower than 5 secs and it makes a backlog of emotions. (gestures just get refused.)
    rospy.Timer(rospy.Duration(secs=5), allowEmotion)

    #This alows us to bypass the 5 sec cooldown if 0(No emotion) is passed through
    rospy.Timer(rospy.Duration(nsecs=500000000), emotionToRobot)#trigggers ever 0.5 secs

   
    
   
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass
