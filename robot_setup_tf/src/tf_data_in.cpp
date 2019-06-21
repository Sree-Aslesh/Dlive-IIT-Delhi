#include <ros/ros.h>
#include "geometry_msgs/Quaternion.h"
#include <tf/transform_broadcaster.h>
#include <nav_msgs/Odometry.h>
#include <sensor_msgs/NavSatFix.h>
#include <math.h>
#include <iostream>
#include <visualization_msgs/Marker.h>

double pose_x=0,pose_y=0;
geometry_msgs::Quaternion odom_quat;
double prev_x=0,prev_y=0,dt,vx,vy,vth;

void get_odom_data(nav_msgs::Odometry msg)
{
  pose_x = msg.pose.pose.position.x;
  pose_y = msg.pose.pose.position.y;

  odom_quat = msg.pose.pose.orientation;
}


int main(int argc, char** argv)
{
  ros::init(argc, argv, "fuse_data");

  ros::NodeHandle n;
  
  ros::Publisher odom_cam0 = n.advertise<nav_msgs::Odometry>("odom_cam_final", 50); 
  ros::Publisher vis_pub = n.advertise<visualization_msgs::Marker>( "visualization_marker", 0 ); 
  ros::Subscriber sub = n.subscribe ( "/odom_cam", 1, get_odom_data );
  
  ros::Time current_time, last_time;
  current_time = ros::Time::now();
  last_time = ros::Time::now();

  tf::TransformBroadcaster odom_broadcaster;
  tf::TransformBroadcaster sensor_broadcaster;
  
  ros::Rate r(1.0);
  while(n.ok()){

    ros::spinOnce();
    current_time = ros::Time::now();
    visualization_msgs::Marker marker;
    marker.header.frame_id = "base_link";
    marker.header.stamp = ros::Time();
    marker.ns = "my_namespace";
    marker.id = 0;
    marker.type = visualization_msgs::Marker::POINTS;
    marker.action = visualization_msgs::Marker::ADD;
    // marker.pose.position.x = pose_x;
    // marker.pose.position.y = pose_y;
    // marker.pose.position.z = 1;
    // marker.pose.orientation.x = odom_quat.x;
    // marker.pose.orientation.y = odom_quat.y;
    // marker.pose.orientation.z = odom_quat.z;
    // marker.pose.orientation.w = odom_quat.w;
    marker.scale.x = 10;
    marker.scale.y = 0.1;
    marker.scale.z = 0.1;
    marker.color.a = 1.0; // Don't forget to set the alpha!
    marker.color.r = 0.0;
    marker.color.g = 1.0f;
    marker.color.b = 0.0;
    geometry_msgs::Point p;
    p.x = pose_x;
    p.y = pose_y;
    p.z = 0;
    marker.points.push_back(p);
    
    vis_pub.publish( marker ); 
    
    geometry_msgs::TransformStamped sensor_trans;
    sensor_trans.header.stamp = current_time;
    sensor_trans.header.frame_id = "base_link";
    sensor_trans.child_frame_id = "sensors_link";

    sensor_trans.transform.translation.x = -2.0;
    sensor_trans.transform.translation.y = 0.0;
    sensor_trans.transform.translation.z = 0.0;
    sensor_trans.transform.rotation = tf::createQuaternionMsgFromYaw(0);

    //send the transform
    odom_broadcaster.sendTransform(sensor_trans); 

    // send Transform from odom -> base - link
    geometry_msgs::TransformStamped odom_trans;
    
    odom_trans.header.stamp = current_time;
    odom_trans.header.frame_id = "odom";
    odom_trans.child_frame_id = "base_link";

    odom_trans.transform.translation.x = pose_x;
    odom_trans.transform.translation.y = pose_y;
    odom_trans.transform.translation.z = 0.0;
    odom_trans.transform.rotation = odom_quat;

    //send the transform
    odom_broadcaster.sendTransform(odom_trans); 

    // odometry msg
    nav_msgs::Odometry odom;
    
    odom.header.stamp = current_time;
    odom.header.frame_id = "odom";

    //set the position
    odom.pose.pose.position.x = pose_x;
    odom.pose.pose.position.y = pose_y;
    odom.pose.pose.position.z = 0.0;
    odom.pose.pose.orientation = odom_quat;
    
    dt = (current_time - last_time).toSec();
    vx = (pose_x - prev_x)/dt;
    vy = (pose_y - prev_y)/dt;
    vth = 0;

    prev_x = pose_x;
    prev_y = pose_y;

    //set the velocity
    odom.child_frame_id = "base_link";
    
    odom.twist.twist.linear.x = vx;
    odom.twist.twist.linear.y = vy;
    odom.twist.twist.linear.z = 0;

    odom.twist.twist.angular.x = 0;
    odom.twist.twist.angular.y = 0;
    odom.twist.twist.angular.z = vth;

                   // check for incoming messages
    odom_cam0.publish(odom);
    last_time = current_time;
    r.sleep();

  }
}
