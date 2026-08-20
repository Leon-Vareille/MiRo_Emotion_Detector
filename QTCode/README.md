Use python version 3.8

In a Ros Noetic workspace, put the qtFaceDetector file in the src file, then run catkin_make on the source of the workspace directory.

Replace any CMakeLists and package.xml files as needed

<h3>Zed i2 camera</h3>

If there's no plans to use the Zed i2 camera, you can remove the line from the launch file that causes the zed i2 camera node to lunch and run. 

Once connected to the QT robot, to use the zed i2 camera you will have to

1. ssh qtrobot@(IP Goes Here)
2. cd Projects/Zed/docker/compose
3. docker compose -f docker-compose-zed.yaml up zed-ros1-lt4 -d
   This can take around 5mins
To swap between using the Zed i2 camera and the in built QT camera, the moveHead.py file will have to be changed slightly. comment / uncomment the unnecessary / necessary subscriber for its respective camera
<h6>(This could perhaps be somewhere to improve upon) </h6>
