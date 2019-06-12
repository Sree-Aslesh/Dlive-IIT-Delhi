#!/usr/bin/env python
import cv2
import geodesy.props
import geodesy.utm
import geodesy.wu_point
import rospy
import numpy as np
import itertools
import socket
import sys
import pickle
from decimal import *
import rospy
import sys, select, termios, tty
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu
import math
import os
import rospkg
from pyquaternion import Quaternion 
from std_msgs.msg import String

class  MapViz(object):
	def __init__(self):
		rospy.loginfo("Map Visualization started...")

		#Initialise topics for ros messages
		imu_topic = "imu_new"
		gps_topic = "gps_new"
		odom_topic = "odom"
		odom_topic2 = "odom_cam"
		odom_topic3 = "odom_final"
		gps_yaw_topic = "gps_yaw"
		self.angle = None
		self.r_matrix = None
		self.initial_lat = 28.5306000
		self.initial_long = 77.1618000
		#redundant variables end.
		self.initial_odom = None
		self.offset_x = None
		self.offset_y = None
		self.vo_orientation = None
		self.vo_orientation1 = None
		self.vo_orientation2 = None
		self.p_initial = geodesy.utm.fromLatLong(self.initial_lat,self.initial_long).toPoint()

		#give the path to map file.
		rp = rospkg.RosPack()
		self.map_file_path = os.path.join(rp.get_path('odom_visualizer'), 'resources', 'map_file.jpg')

		#load it as an opencv image 
		self.map_img = cv2.imread(self.map_file_path,cv2.IMREAD_COLOR)
		self.first_msg_received = False
		self.first_x = None
		self.first_y = None
		self.dist_x = None
		self.dist_y = None
		self.last_odom_x = None
		self.last_odom_y = None
		self.last_odom_x1 = None
		self.last_odom_y1 = None
		self.last_odom_x2 = 0
		self.last_odom_y2 = 0
		self.last_gps = None
		self.gps_yaw = None

		#rospy.loginfo("imuReceived assigned successfully during initialise...")
		#opencv window declaration.
		self.cv_window = cv2.namedWindow("MapDisplay",0)

		#Subsribing to topics
		self.vo_odom_sub1 =  rospy.Subscriber('/'+ odom_topic, Odometry, self.odom_cb, queue_size=100)
		self.vo_odom_sub2 =  rospy.Subscriber('/'+ odom_topic2, Odometry, self.odom_cb2, queue_size=100)
		self.vo_odom_sub3 =  rospy.Subscriber('/'+ odom_topic3, Odometry, self.odom_cb3, queue_size=100)
		self.gps_sub = rospy.Subscriber('/'+gps_topic, NavSatFix, self.gps_cb, queue_size=100)
		self.gps_yaw_sub = rospy.Subscriber('/'+ gps_yaw_topic, Imu , self.gps_yaw_cb, queue_size=100)

		#Getting initial pose

		rospy.loginfo("Waiting for IMU message for initial pose")
		message = rospy.wait_for_message("/"+imu_topic, Imu)
		imu_data = message
		print (imu_data)
		'''
		self.splitStrings= str(message.data).split(",")
		self.splitStrings2= str(message.data).split(",")
		'''
		imu_x= imu_data.orientation.x
		imu_y=imu_data.orientation.y
		imu_z=imu_data.orientation.z
		imu_w=imu_data.orientation.w
		self.initial_pose = Quaternion(imu_x,imu_y,imu_z,imu_w).inverse
		rospy.loginfo("IMU data received")

		#Waiting for GPS signals
		rospy.loginfo("Waiting for GPS signals")
		while self.last_gps == None:
			rospy.sleep(0.020)
		p = geodesy.utm.fromLatLong(self.last_gps.latitude,self.last_gps.longitude).toPoint()

		self.offset_x = p.x-self.p_initial.x
		self.offset_y = p.y-self.p_initial.y

	def odom_cb(self, data):
		#print "in if block"
		self.last_odom_x = data.pose.pose.position.x
		self.last_odom_y = data.pose.pose.position.y
		self.vo_orientation = Quaternion(data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z, data.pose.pose.orientation.w ).inverse
		#self.first_x = data.pose.pose.position.x
		#self.first_y = data.pose.pose.position.y

	def odom_cb2(self, data):
		#print "in if block"
		self.last_odom_x1 = data.pose.pose.position.x
		self.last_odom_y1 = data.pose.pose.position.y
		self.vo_orientation1 = Quaternion(data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z, data.pose.pose.orientation.w )#.inverse
	
	def odom_cb3(self, data):
		self.last_odom_x2 = data.pose.pose.position.x
		self.last_odom_y2 = data.pose.pose.position.y
		self.vo_orientation2 = Quaternion(data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z, data.pose.pose.orientation.w )#.inverse
	    

	def gps_cb(self, data):
		self.last_gps = data

	def gps_yaw_cb(self, data):
		self.gps_yaw = Quaternion(data.orientation.x, data.orientation.y, data.orientation.z, data.orientation.w).inverse


	#for all the computations.
	def do_work(self):

		

		p = geodesy.utm.fromLatLong(self.last_gps.latitude,self.last_gps.longitude).toPoint()

		self.dist_x = p.x-self.p_initial.x
		self.dist_y = p.y-self.p_initial.y

		#self.last_odom_x1 = self.dist_x

		c0= self.initial_pose.rotate([self.last_odom_x, self.last_odom_y, 0])
		c1= self.initial_pose.rotate([self.last_odom_x1, self.last_odom_y1, 0])
		c2= self.initial_pose.rotate([self.last_odom_x2, self.last_odom_y2, 0])
		
		corrected_coordinates = np.array([[c0[0]],[c0[1]],[c0[2]]])
		corrected_coordinates1 = np.array([[c1[0]],[c1[1]],[c1[2]]])
		corrected_coordinates2 = np.array([[c2[0]],[c2[1]],[c2[2]]])

		self.angle = math.radians(90)
		r_matrix1 = np.array([[math.cos(self.angle) , -math.sin(self.angle) , 0],[math.sin(self.angle) , math.cos(self.angle) , 0],[0 , 0 , 1]])

		self.angle = math.radians(-110)
		r_matrix2 = np.array([[math.cos(self.angle) , -math.sin(self.angle) , 0],[math.sin(self.angle) , math.cos(self.angle) , 0],[0 , 0 , 1]])

		self.angle = math.radians(-90)
		r_matrix3 = np.array([[math.cos(self.angle) , -math.sin(self.angle) , 0],[math.sin(self.angle) , math.cos(self.angle) , 0],[0 , 0 , 1]])


		corrected_coordinates = np.dot(r_matrix1,corrected_coordinates)#*r_matrix
		corrected_coordinates1 = np.dot(r_matrix2,corrected_coordinates1)
		corrected_coordinates2 = np.dot(r_matrix3,corrected_coordinates2)

		#print 'corrected_coordinates are '
		print corrected_coordinates
		print np.shape(corrected_coordinates)

		if self.offset_x + self.last_odom_x >=0 and self.offset_x + self.last_odom_x < 7164 and self.offset_y + self.last_odom_y>=0 and self.offset_y + self.last_odom_y< 3358:
			cv2.circle(self.map_img,(int(p.x-self.p_initial.x),int(p.y-self.p_initial.y)),1,(0,255,0),-1)
		
		if self.offset_x +self.last_odom_x >=0 and self.offset_x+ self.last_odom_x < 7164 and self.offset_y+self.last_odom_y>=0 and self.offset_y+self.last_odom_y< 3358:
			cv2.circle(self.map_img,(int(self.offset_x+corrected_coordinates[0]),int(self.offset_y+corrected_coordinates[1])),1,(0,0,255),-1)

		if self.offset_x +self.last_odom_x1 >=0 and self.offset_x + self.last_odom_x1 < 7164 and self.offset_y + self.last_odom_y1>=0 and self.offset_y+self.last_odom_y1< 3358:
			cv2.circle(self.map_img,(int(self.offset_x+corrected_coordinates1[0]),int(self.offset_y+corrected_coordinates1[1])),1,(255,20,20),-1)			
		
		if self.offset_x +self.last_odom_x2 >=0 and self.offset_x + self.last_odom_x2 < 7164 and self.offset_y + self.last_odom_y2>=0 and self.offset_y+self.last_odom_y2< 3358:
			cv2.circle(self.map_img,(int(self.offset_x+corrected_coordinates2[0]),int(self.offset_y+corrected_coordinates2[1])),1,(255,180,180),-1)

		# if self.offset_x +self.last_odom_x1 >=0 and self.offset_x + self.last_odom_x1 < 7164 and self.offset_y +self.last_odom_y1>=0 and self.offset_y+self.last_odom_y1< 3358:
		# 	corrected_coordinates1 = self.initial_pose.rotate([self.last_odom_x1, self.last_odom_y1, 0])
		# 	cv2.circle(self.map_img,(int(self.offset_x+corrected_coordinates1[0]),int(self.offset_y+corrected_coordinates1[1])),1,(255,0,0),-1)
		# 	if self.gps_yaw != None:
		# 		temp = self.vo_orientation.rotate([self.last_odom_x, self.last_odom_y, 0])
		# 		corrected_coordinates_gps = self.gps_yaw.rotate(temp)
		# 		cv2.circle(self.map_img,(int(self.offset_x+corrected_coordinates_gps[0]),int(self.offset_y+corrected_coordinates_gps[1])),1,(255,0,0),-1)

		cv2.imshow("MapDisplay", self.map_img)
		cv2.waitKey(1)

	def run(self):
		r = rospy.Rate(1)
		while not rospy.is_shutdown():
			self.do_work()
			r.sleep()

if __name__ =='__main__':
	rospy.init_node('map_visualization')
	viz = MapViz()
	viz.run()


	

