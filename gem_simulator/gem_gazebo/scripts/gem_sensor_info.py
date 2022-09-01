#!/usr/bin/env python3

#================================================================
# File name: gem_sensor_info.py                                                                  
# Description: show sensor info in Rviz                                                              
# Author: Hang Cui
# Email: hangcui3@illinois.edu                                                                     
# Date created: 06/10/2021                                                                
# Date last modified: 07/02/2021                                                          
# Version: 0.1                                                                    
# Usage: rosrun gem_gazebo gem_sensor_info.py                                                                     
# Python version: 3.8                                                             
#================================================================

# Python Headers
import math
import random
import numpy as np

# ROS Headers
import rospy
from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import Twist, Vector3
from jsk_rviz_plugins.msg import OverlayText
from std_msgs.msg import ColorRGBA, Float32
from tf.transformations import euler_from_quaternion, quaternion_from_euler

# Gazebo Headers
from gazebo_msgs.srv import GetModelState
from gazebo_msgs.msg import ModelState


class GEMOverlay(object):

    def __init__(self):
          
        self.sensor_info_pub = rospy.Publisher("/gem/sensor_info", OverlayText, queue_size=1)
        self.gps_sub         = rospy.Subscriber("/gps/fix", NavSatFix, self.gps_callback)
        self.imu_sub         = rospy.Subscriber("/imu", Imu, self.imu_callback)
        self.rate            = rospy.Rate(10)

        self.sensor_overlaytext = self.update_sensor_overlaytext()
        self.sensor_info_update = False

        self.lat         = 0.0
        self.lon         = 0.0
        self.alt         = 0.0
        self.imu_yaw     = 0.0

        self.x          = 0.0
        self.y          = 0.0
        self.x_dot      = 0.0
        self.y_dot      = 0.0
        self.gazebo_yaw = 0.0


    def gps_callback(self, msg):
        self.lat = round(msg.latitude, 6)
        self.lon = round(msg.longitude, 6)
        self.alt = round(msg.altitude, 6)


    def imu_callback(self, msg):
        orientation_q      = msg.orientation
        angular_velocity   = msg.angular_velocity
        linear_accel       = msg.linear_acceleration
        orientation_list   = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, yaw) = euler_from_quaternion(orientation_list)
        self.imu_yaw       = round(yaw, 6)   


    def get_gem_state(self):

        rospy.wait_for_service('/gazebo/get_model_state')
        
        try:
            service_response = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            model_state = service_response(model_name='gem')
        except rospy.ServiceException as exc:
            rospy.loginfo("Service did not process request: " + str(exc))

        x = model_state.pose.position.x
        y = model_state.pose.position.y

        orientation_q    = model_state.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]

        # roll: x-axis,  pitch: y-axis, yaw: z-axis
        (roll, pitch, yaw) = euler_from_quaternion(orientation_list)

        x_dot = model_state.twist.linear.x
        y_dot = model_state.twist.linear.y

        return round(x,3), round(y,3), round(yaw,3), round(x_dot,3), round(y_dot,3)


    def update_sensor_overlaytext(self, lat=0.0, lon=0.0, alt=0.0, imu_yaw=0.0, x=0.0, y=0.0, gazebo_yaw=0.0, x_dot=0.0, y_dot=0.0, f_vel=0.0):

        text            = OverlayText()
        text.width      = 230
        text.height     = 290
        text.left       = 10
        text.top        = 10
        text.text_size  = 12
        text.line_width = 2
        text.font       = "DejaVu Sans Mono"
        text.text       = """----------------------
                             Sensor (Measurement):
                             Lat = %s
                             Lon = %s
                             Alt = %s
                             Yaw = %s
                             ----------------------
                             Gazebo (Ground Truth):
                             X     = %s
                             Y     = %s
                             X_dot = %s
                             Y_dot = %s
                             F_vel = %s
                             Yaw   = %s
                             ----------------------
                          """ % (str(lat), str(lon), str(alt), str(imu_yaw), str(x), str(y), str(x_dot), str(y_dot), str(f_vel), str(gazebo_yaw))
        text.fg_color   = ColorRGBA(25 / 255.0, 1.0, 240.0 / 255.0, 1.0)
        text.bg_color   = ColorRGBA(0.0, 0.0, 0.0, 0.2)
        return text
    

    def update_sensor_overlaytext_only(self, new_text):
        self.sensor_overlaytext.text = new_text


    def start_demo(self):
        
        while not rospy.is_shutdown():

            self.x, self.y, self.gazebo_yaw, self.x_dot, self.y_dot = self.get_gem_state()

            f_vel = round(np.sqrt(self.x_dot**2 + self.y_dot**2), 3)

            if(self.sensor_info_update):
                sensor_text = """----------------------
                                 Sensor (Measurement):
                                 Lat = %s
                                 Lon = %s
                                 Alt = %s
                                 Yaw = %s
                                 ----------------------
                                 Gazebo (Ground Truth):
                                 X_pos = %s
                                 Y_pos = %s
                                 X_dot = %s
                                 Y_dot = %s
                                 F_vel = %s
                                 Yaw   = %s
                                 ----------------------                               
                              """ % ( str(self.lat), str(self.lon), str(self.alt), str(self.imu_yaw), \
                                      str(self.x), str(self.y), str(self.x_dot), str(self.y_dot), str(f_vel), str(self.gazebo_yaw))
                self.update_sensor_overlaytext_only(sensor_text)
            else:
                self.sensor_overlaytext = self.update_sensor_overlaytext()
                self.sensor_info_update = True

            self.sensor_info_pub.publish(self.sensor_overlaytext)

            self.rate.sleep()
  
  
def gem_overlay():

    rospy.init_node('gem_sensor_info', anonymous=True)

    gem_overlay_object = GEMOverlay()

    try:
        gem_overlay_object.start_demo()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    gem_overlay()