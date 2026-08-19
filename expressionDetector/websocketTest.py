import roslibpy

import time

import cv2
import numpy as np
import os
from huggingface_hub import InferenceClient
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
import matplotlib.pyplot as plt


print("Attempting to connect to Ros...")
client = roslibpy.Ros(host='192.168.1.28', port=9999)
client.run()
print("Ros setup!")



print("Initilising the expression VLA")

"""
processor = AutoImageProcessor.from_pretrained("shrestha1/vit-Facial-Expression-Recognition")
model = AutoModelForImageClassification.from_pretrained("shrestha1/vit-Facial-Expression-Recognition", device_map="auto")
#"""

#"""
processor = AutoImageProcessor.from_pretrained("Alpiyildo/vit-Facial-Expression-Recognition")
model = AutoModelForImageClassification.from_pretrained("Alpiyildo/vit-Facial-Expression-Recognition")
#"""
os.environ['07/07token'] = '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'

VLM = InferenceClient(
    provider="auto",
    api_key=os.environ['07/07token'],
    )
print("VLA modle setup!")


def showEye(eyetxt,frame):
    #Saves the frame as a jpg
    cv2.imwrite(eyetxt+".jpg",frame)
    cv2.imshow(eyetxt, frame)
    
    return (eyetxt+".jpg")



def callback(data, height, width):
    print("Recieved data")
    
    data = np.array(list(data))

    """This is for a Coloured img
    #it is in a 1D array, now onto a 3D array
    frame = data.reshape(height,width,3)
    #"""

    #"""This is for a Gray img
    #it is in a 1D array, now onto a 2D array
    frame = data.reshape(height,width)
    #"""
    



    """We have the frame as a usable array
    if eye==1:
        #We have the left eye
        imgToUse = showEye("LeftEye", frame)
    else:
        #We have the right eye
        imgToUse = showEye("RightEye", frame)

    #"""

    imgToUse = showEye("BothEye", frame)

 
    faceImg = None
    faceImg = cv2.imread(imgToUse)
    try:
        #cv2.imshow("full face w/ kp", faceImg)
        pass
    except:
        pass



    image = Image.open(imgToUse)
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad(): outputs = model(**inputs)
    
    predicted_class = outputs.logits.argmax(dim=-1).item()
  
    #We need to publish predicted_class to /emotion
    emotionSender.publish(roslibpy.Message({'data' : predicted_class}))
    
    print(predicted_class)



try:
    emotionSender = roslibpy.Topic(client, "/emotion","std_msgs/Int8")
    posSender = roslibpy.Topic(client,"/position","std_msgs/Float32MultiArray")

    getImgService = roslibpy.Service(client,"/ImgService","emotion_detector/returnFrame")
    request = roslibpy.ServiceRequest()

    while(1):
        try:

            print("Trying to get frame...")
            start = time.perf_counter()
            frame = None
            try:
                frame = getImgService.call(request)
            except:
                pass
            if frame == None:
                continue

            
            callback(frame["frameInTheSrv"], frame["height"], frame["width"])
            cv2.waitKey(1)
            end = time.perf_counter()
            print("Time for callback: ",end - start)
        except KeyboardInterrupt:
            client.terminate()
            break
             

except KeyboardInterrupt:
    client.terminate()





"""
we want a sercive that returns the curently saved frame from cv2Frame as a float32MultiArray
frame = getImgService
callback(frame)
"""


""" #Testing publishing directly to the cosmetic joints topic:
testCos = roslibpy.Topic(client, "/miro/control/cosmetic_joints","std_msgs/Float32MultiArray")
testCos.publish(roslibpy.Message({"data" : [0,0,0,0,0,0]}))
print("Published to cosmetic joints")
"""# it works as intended

