#!/usr/bin/env python

"""
A python program to recieve an emotion in the form of a number,
then forward that message onwards

subscribes to:
    /emotion


Publishes to:
    /Mito/control/cosmetic_joints
"""

import random
import wave
import numpy as np

import rospy
from std_msgs.msg import UInt16MultiArray, Int16MultiArray
from std_msgs.msg import Int8
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState
from miro2_msg.msg import animal_state



#It holds the preveious emotion and the timer for its reset
prevEmotion = [None,0]
prevTime =[0,0]
allowEmotionUpdate = True

eyelid = [0,0]
eyelidLevels = [0.15,0.15]

cReady = True

#        [[old c joints],                 [current c joints],             [new c joints],                  [time for tranformation]]
Joints = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  [1.0, 0]]



def callbackTimer(data):
    #print("Timer triggered")
    global prevEmotion

    prevEmotion[1] +=1
    if prevEmotion[1] >= 20:
        callback(-1)

    

def callback(emotion):
    global prevEmotion
    global allowEmotionUpdate


    if isinstance(emotion, int):
        pass #If callback is triggered via callbackTimer, itll go here and continue as normal as emotion is passesd through as a usable int
    else:
        #Transform the Int8 into a more usable int 
        emotion = int(emotion.data)
    

    if prevEmotion[0] != emotion and allowEmotionUpdate:
        
    
        prevEmotion[0] = emotion
        prevEmotion[1] = 0
        allowEmotionUpdate = False
        rospy.Timer(rospy.Duration(1,0), updateAllowEmotionUpdate, oneshot=True)
    
    setJoints(prevEmotion[0])
        


    

  

def happy():
    global prevTime
    global cReady

    global eyelid
    

    global Joints
    #[[old c joints], [current c joints], [new c joints],[time for tranformation]]
    
    
    #Cosmetic joints
    #print("Tail wag dir: ", prevTime)
    if cReady:
        if prevTime:
            prevTime = 0
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]

            Joints[2] = [0.5,0.6,eyelid[0],eyelid[1],0.35,0.35]
            Joints[3][0] =0.5
        
        else:
            prevTime = 1
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]

            Joints[2] = [0.5,0,eyelid[0],eyelid[1],0.35,0.35]
            Joints[3][0] =0.5
            




def sad():
    global prevTime
    global cReady
    global eyelid

    global Joints
    #[[old c joints], [current c joints], [new c joints],[time for tranformation]]



   #Cosmetic joints
    if cReady:
        if prevTime==1:
            prevTime = 0
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]

            Joints[2] = [0,0.5,eyelid[0],eyelid[1],-1,-1]
            Joints[3][0] = 1
        
        elif prevTime==0:

            rand = random.randint(1, 10)
            if rand == 1:
                prevTime=2
            else:
                prevTime=1
            
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]

            Joints[2] = [0,0.5,eyelid[0],eyelid[1],1,1]
            Joints[3][0] = 1

        elif prevTime==2:
            prevTime = 1
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]

            Joints[2] = [0,0.5,eyelid[0],eyelid[1],0.3,0.3]
            Joints[3][0] = 0.2



def chill():
    global prevTime
    global cReady
    global eyelid

    global Joints
    #[[old c joints], [current c joints], [new c joints],[time for tranformation]]

    
    #Cosmetic joints
    #print("Tail wag dir: ", prevTime)
    if cReady:
        if prevTime:
            prevTime = 0
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]
            
            Joints[2] = [0.5,0.6,eyelid[0],eyelid[1],0.35,0.35]
            Joints[3][0] = 1
        
        else:
            prevTime = 1
            cReady = 0

            #update the old cJoints
            Joints[0] = Joints[2]

            Joints[2] = [0.5,0,eyelid[0],eyelid[1],0.35,0.35]
            Joints[3][0] = 1



def angry():
    global prevTime
    global cReady
    global Joints
    print(prevTime)
    if prevTime:
        prevTime = 0
        time = random.randint(4, 7)
        rospy.Timer(rospy.Duration(time,0), woof, oneshot=True)


    #set the cosmetic joints
    if cReady:
        cReady = 0
        #update the old joints
        Joints[0] = Joints[2]

        
        Joints[2] = [-1.0,0.4, 0.0, 0.0, 0.0, 0.0]
        Joints[3][0] = 1




def woof(data):
    global prevTime
    prevTime = 1
    print('WOOF')
    #we need to publish to tone
    msg = UInt16MultiArray()
    streamMsg = Int16MultiArray()
    
    streamPub = rospy.Publisher("/miro/control/stream", Int16MultiArray, queue_size=1)
    pub = rospy.Publisher("/miro/control/tone", UInt16MultiArray, queue_size=1)
  
    durSecs = 0.25

    
    audio = (150, 255, int((durSecs*1000)/20))
    pub.publish(msg.layout, audio)

    """
    print("Opening wav file")
    w = wave.open("dogBark.wav", "r")

    samples = w.getnframes()
    audio = w.readframes(samples)

    # convert to numpy array
    waves = np.frombuffer(audio, dtype=np.int16)
    
    print("Publishing to stream")
    streamPub.publish(streamMsg.layout, waves[1100:5100])
    #"""


   
   


def updateAllowEmotionUpdate(data):
    global allowEmotionUpdate
    allowEmotionUpdate = True


def setJoints(emotion):
    global eyelidLevels
     
    #emotion = -1
    
    print("Passing through", emotion)
    eyelidLevels = [0.05, 0.05]
    if emotion == 0:#Angry
        eyelidLevels = [0.0,0.0]
        angry()
        
    elif emotion == 1:#Disgusted
        chill()
        
    elif emotion == 2:#Fearful
        chill()
        
    elif emotion == 3:#Happy
        happy()

    elif emotion == 4:#Sad
        sad()

    elif emotion == 5:#Surprised
        chill()
        
    elif emotion == 6:#Neutral
        chill()
        
    else:#Defualt
        chill()
        

    




def blinkCallback(data):
    def reopenEye(data):
        #print("Let there be light")
        global eyelid
        global eyelidLevels
        eyelid = [eyelidLevels[0],eyelidLevels[1]]

    global eyelid
    #print("ITS DARK")

    #eyelid = [1.0,1.0]
    rospy.Timer(rospy.Duration(0,500000000), reopenEye, oneshot=True)








def smoothMovements(data):
    global eyelid
    global cReady

    global Joints
    #[[old c joints], [current c joints], [new c joints],[time for tranformation]]

 

    #Loop for c joints 
    for i in range (0,6):
        #current = ((new - old)/(timefortransrofmation*100))*currentStep
        Joints[1][i] = ((Joints[2][i] - Joints[0][i])/(Joints[3][0]*100))*Joints[3][1]

    #Validation for tail joint value
    lowerLimit = 0.15
    if Joints[1][1] <lowerLimit:
        Joints[1][1] = lowerLimit
    
    
    #"""
    #update the eyes independantly
    Joints[1][2] = eyelid[0]
    Joints[1][3] = eyelid[1]
    #"""


    #Setting the cosmetic joints
    msg = Float32MultiArray
    layout = msg().layout

    cosJ = rospy.Publisher('/miro/control/cosmetic_joints', 
                                Float32MultiArray, 
                                queue_size=1)
    
    cosJ.publish(layout, Joints[1])
   

    Joints[3][1] +=1



    if Joints[3][1] >= Joints[3][0]*100:
        cReady=1
        Joints[3][1] = 0













if __name__ == "__main__":
    try:
        rospy.init_node('emotionToJoints') 
        print("emotionToJoint node initilised")

        reRunTime = rospy.Duration(nsecs=125000000) #should trigger 8 times a second (every 125,000,000 nano seconds)
        eyeBlinkTimer = rospy.Duration(4)
        smoothingTimer = rospy.Duration(nsecs=10000000) #should trigger 100 times a second
       
        

        try:
        
        
            rospy.Subscriber('/emotion', Int8, callback)

            #We want the robot to blink periodically
            rospy.Timer(eyeBlinkTimer, blinkCallback)

            rospy.Timer(smoothingTimer, smoothMovements)
            

            #The timer helps ensure that the same emotion is showed even when no image is being passed through
            rospy.Timer(reRunTime, callbackTimer)
                
            rospy.spin()
        
        except KeyboardInterrupt():
                pass
    except rospy.ROSInternalException:
        pass
