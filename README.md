# Dlive IIT Delhi

Dlive stands for Driver-less Intelligent Vehicle. This project was done a part of Mahindra's Autonomous driving challenge. It was done during my Internship at IIT Delhi under the guidance of Dr. Sunil Kr. Jha in the summer of 2018.

<p align="center">
  <img width="460" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/media/19366210_1933167820259677_9058465279413749139_n.jpg">
</p>

The main objective was to obtain the odometry from the sensors and plot it initially by developing a package called odom map viz.THis package takes the odometry as input and plots them on a static map.

### Odom map Viz
This is the package using a static map to visualize the odometry of the vehicle while moving. The static map is given below.

<p align="center">
  <img width="600" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/odom_map_viz/resources/map_file.jpg">
</p>

This static map plotting is done by taking one orner of the map as reference while dividing the co-rodinate segmentation of latitude and longitude acriss x and y axis. Based on this when a co-ordinate is given, the program first verifies if the given co-ordinate exists in the range given by the static map. If it does exist it divided the difference of the latitudes and logitueds by their respective ranges givin the proportion of the map. This proportion is converted into the distance in pixels and the popint is plotted. a sample plot is given below

<p align="center">
  <img width="600" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/odom_map_viz/resources/map_example.png">
</p>

### Obtaining Odometry

Hardware being used -
  1. 10 DOF IMU
  2. GPS (Ublox 7m)
  3. Zed stereo camera
 
GPS basically gives the position so it was plotted as is. Computation of movement between two consecutive messages was being done for IMU. For each message the timestamp was being considered and based on the twist of the latter imu message the distance of movement was being calculated. For visual odometry purposes, Zed ros wrapper was being used which gave data with a certain amount of drift. The image given below better shows this situation when we were facing this problem. 

<p align="center">
  <img width="460" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/media/IMG_20180524_175534.jpg">
</p>


So, ORB-SLAM was used.

### Visual Odometry - Orb SLAM

Visual odometry is being obtained from ORB SLAM algorithm with zed stereo camera's images as its input. Screen Shots of the algorithm during testing have been attached below.

<p align="center">
  <img width="400" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/media/Screenshot%20from%202018-06-24%2015-08-30.png">
  <img width="400" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/media/Screenshot%20from%202018-06-24%2015-08-22.png">
</p>

Orb slam does not give out its pose as a message. It runs as a standalone node with its own plotting of map. This became a problem as we were going to integrate this with the robot loalization package for higher computational accuracy. For this purpose we had to find the file in which all the computation for pose was being done and change the file such that it publishes a ros message of type odom so that we can use it for localization and visualizaton of odometry. Plots of all the different types of odometry obtained have beem plotted on the same static map for refererence and it is given below.



<p align="center">
  <img width="460" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/media/Screenshot%20from%202018-06-08%2010-02-38.png">
</p>

A live example of the orb slam implementation is given below

<p align="center">
  <img width="460" height="300" src="https://github.com/Sree-Aslesh/Dlive-IIT-Delhi/blob/master/media/orbslam.gif">
</p>



