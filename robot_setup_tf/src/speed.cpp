
#include <ros/ros.h>
#include <math.h>
#include <iostream>
#include "sensor_msgs/Imu.h"
#include "std_msgs/Float32.h"
#include "nav_msgs/Odometry.h"
#include <fstream>
int flag=0;


using namespace std;
double time_prev,time_curr,delta;

float linear_accel_x=0,linear_accel_y=0,linear_accel_z=0;
float linear_vel_x=0,linear_vel_y=0,linear_vel_z=0;
int x=0,y=0,z=0;
int x_cam=0,y_cam=0,z_cam=0;

void odom_callback(nav_msgs::Odometry msg)
{
	x = msg.pose.pose.position.x;
	y = msg.pose.pose.position.y;
	z = msg.pose.pose.position.z;

}

void odom_cam_callback(nav_msgs::Odometry msg)
{
	x_cam = msg.pose.pose.position.x;
	y_cam = msg.pose.pose.position.y;
	z_cam = msg.pose.pose.position.z;

}


// void imu_callback(sensor_msgs::Imu msg)
// {
//     linear_accel_x=msg.linear_acceleration.x;
//     linear_accel_y=msg.linear_acceleration.y;
//     linear_accel_z=msg.linear_acceleration.z;

//     time_curr=ros::Time::now().toSec();
//     delta = time_curr - time_prev;
    
//     linear_vel_x = (linear_vel_x + linear_accel_x *delta)*5/18;
//     linear_vel_y = (linear_vel_y + linear_accel_y *delta)*5/18;
//     linear_vel_z = (linear_vel_z + linear_accel_z *delta)*5/18;

// }


int main(int argc, char **argv)
{
    ros::init(argc, argv, "speed_node");
    ros::start();
    time_prev =ros::Time::now().toSec();

    ros::NodeHandle nh;
    

    //ros::Subscriber imu_sub=nh.subscribe("/imu_new",1000,imu_callback);
    ros::Subscriber odom_sub=nh.subscribe("/odom",1000,odom_callback);
    ros::Subscriber odom_cam_sub=nh.subscribe("/odom_cam",1000,odom_cam_callback);
    // ros::Publisher speed_pub_x = nh.advertise<std_msgs::Float32>("speed_x", 100);
    // ros::Publisher speed_pub_y = nh.advertise<std_msgs::Float32>("speed_y", 100);
    // ros::Publisher speed_pub_z = nh.advertise<std_msgs::Float32>("speed_z", 100);
    ros::Rate r(30);
    ofstream odom;
    ofstream odom_cam;
    odom_cam.open ("orb_data.csv");
    odom.open ("zed_data.csv");
while(ros::ok())
  { 
   // std_msgs::Float32 speed_x;
   // std_msgs::Float32 speed_y;
   // std_msgs::Float32 speed_z; 
   // speed_x.data = linear_vel_x;
   // speed_y.data = linear_vel_y;
   // speed_z.data = linear_vel_z;
   // speed_pub_x.publish(speed_x);
   // speed_pub_y.publish(speed_y);
   // speed_pub_z.publish(speed_z);
   // cout >> "X - " >>  linear_vel_x >> "  Y - " >> linear_vel_y >> "  Z - " >> linear_vel_z >> endl;
   // ROS_INFO("x_vel = %f, y_vel= %f , z_vel = %f", linear_vel_x,linear_vel_y,linear_vel_z);
   // ROS_INFO(" z_vel= %f ",linear_vel_z);

	odom_cam << x_cam;
	odom_cam << ",";
	odom_cam << y_cam; 
	odom_cam << ",";
	odom_cam << z_cam;
	odom_cam << ",\n";

	odom << x;
	odom << ",";
	odom << y; 
	odom << ",";
	odom << z;
	odom << ",\n";
   ros::spinOnce();
   r.sleep();
}
return 0;
}

       

  
