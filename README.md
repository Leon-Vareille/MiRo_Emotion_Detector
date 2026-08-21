# MiRo_Emotion_Detector

Both the miroCode and the QTCode have been ran through a docker compose with the necessary robot code installed (miro MDK/ QTrobot SDK) and APIs. The docker has a volume allowing code to be stored and saved on the PC so the workspace isn't reset ever time the robot is turned off and on again. 


<br>
<br>
<h2>miroCode</h2>

Split into two, based on the required python version.

Built through Ros Noetic and using a ros bridge websocket to connect to the higher python version(3.12) and extra python script.

This system works with the MiRo-E robots and the MDK from consequential robotics to implement emotion detection into the robot as well as person following.

VLM Modles from LeRobot as well as Microsoft MediaPipe were used to implement these functions


<br>
<br>
<h2>QTCode</h2>

very similar to the miro, but using the QT robots from luxai instead

<h3>Zed i2 camera</h3>
To use the zed i2 camera, the git for the camera will have to be installed into the src of the workspace for the code. it will be its own package, it can be found at:
https://github.com/stereolabs/zed-ros-interfaces.git



<br>
<br>
<h2>expressionDetector</h2>
Taking in an image to be passed to the VLM that will detect facial expressions, and then will return the facial expression as a number. 
It is used as a service in the ros system, though it requires the rosbridge, and the rosbridge to be sourced in the workspace of the miro/QT code to work
