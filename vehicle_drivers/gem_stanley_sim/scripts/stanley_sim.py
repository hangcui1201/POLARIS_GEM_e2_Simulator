#!/usr/bin/env python3

#================================================================
# File name: stanley_sim.py                                                                  
# Description: stanley controller for GEM vehicle in Gazebo                                                              
# Author: Hang Cui
# Email: hangcui3@illinois.edu                                                                     
# Date created: 07/10/2021                                                                
# Date last modified: 07/15/2021                                                          
# Version: 0.1                                                                    
# Usage: rosrun gem_stanley_sim stanley_sim.py                                                                    
# Python version: 3.8                                                             
#================================================================

# Python Headers
import os 
import csv
import math
import numpy as np
from numpy import linalg as la

# ROS Headers
import rospy
from ackermann_msgs.msg import AckermannDrive
from geometry_msgs.msg import Twist, Vector3
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import LaserScan
from tf.transformations import euler_from_quaternion, quaternion_from_euler

# Gazebo Headers
from gazebo_msgs.srv import GetModelState
from gazebo_msgs.msg import ModelState


class Stanley(object):
    
    def __init__(self):

        self.rate       = rospy.Rate(20)
        self.wheelbase  = 1.75 # meters

        self.read_waypoints() # read waypoints

        self.ackermann_msg = AckermannDrive()
        self.ackermann_msg.steering_angle_velocity = 0.0
        self.ackermann_msg.acceleration            = 0.0
        self.ackermann_msg.jerk                    = 0.0
        self.ackermann_msg.speed                   = 0.0 
        self.ackermann_msg.steering_angle          = 0.0

        self.ackermann_pub = rospy.Publisher('/ackermann_cmd', AckermannDrive, queue_size=1)

    def read_waypoints(self):

        dirname  = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../waypoints/wps.csv')

        with open(filename) as f:
            path_points = [tuple(line) for line in csv.reader(f)]

        self.path_points_x   = [float(point[0]) for point in path_points]
        self.path_points_y   = [float(point[1]) for point in path_points]
        self.path_points_yaw = [float(point[2]) for point in path_points]
        self.dist_arr        = np.zeros(len(self.path_points_x))


    def get_gem_state(self):

        rospy.wait_for_service('/gazebo/get_model_state')
        
        try:
            service_response = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            model_state = service_response(model_name='gem')
        except rospy.ServiceException as exc:
            rospy.loginfo("Service did not process request: " + str(exc))

        x = model_state.pose.position.x
        y = model_state.pose.position.y

        orientation_q      = model_state.pose.orientation
        orientation_list   = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, yaw) = euler_from_quaternion(orientation_list)

        x_dot = model_state.twist.linear.x
        y_dot = model_state.twist.linear.y

        return round(x,4), round(y,4), round(x_dot,4), round(y_dot,4), round(yaw,4)


    def pi_2_pi(self, angle):

        if angle > math.pi:
            return angle - 2.0 * math.pi
        if angle < -math.pi:
            return angle + 2.0 * math.pi

        return angle


    def start_stanley(self):
        
        while not rospy.is_shutdown():

            # get current position and orientation in the world frame
            # reference point is located at the center of rear axle
            curr_x, curr_y, curr_x_dot, curr_y_dot, curr_yaw = self.get_gem_state()

            # reference point is located at the center of frontal axle
            front_x = self.wheelbase*np.cos(curr_yaw) + curr_x
            front_y = self.wheelbase*np.sin(curr_yaw) + curr_y

            # find the closest point
            dx = [front_x - x for x in self.path_points_x]
            dy = [front_y - y for y in self.path_points_y]

            # find the index of closest point
            target_index = int(np.argmin(np.hypot(dx, dy)))

            front_axle_vec_rot_90 = np.array([[math.cos(curr_yaw - math.pi / 2.0)],
                                              [math.sin(curr_yaw - math.pi / 2.0)]])

            vec_target_2_front = np.array([[dx[target_index]], [dy[target_index]]])
            
            # crosstrack error
            ef = np.dot(vec_target_2_front.T, front_axle_vec_rot_90)
            ef = float(np.squeeze(ef))

            # vehicle heading 
            theta = curr_yaw

            # approximate heading of path at (path_x, path_y)
            path_x      = self.path_points_x[target_index]
            path_y      = self.path_points_y[target_index]
            path_x_next = self.path_points_x[target_index+1]
            path_y_next = self.path_points_y[target_index+1]
            theta_p     = np.arctan2(path_y_next-path_y, path_x_next-path_x)

            # theta_e is the heading error
            theta_e = self.pi_2_pi(theta_p-theta)

            f_vel = round(np.sqrt(curr_x_dot**2 + curr_y_dot**2), 3)

            delta = round(theta_e + math.atan2(0.45 * ef, f_vel), 3)

            theta_e  = round(np.degrees(theta_e), 1)

            ef = round(ef,3)
            print("Crosstrack Error: " + str(ef) + ", Heading Error: " + str(theta_e))

            # implement constant pure pursuit controller
            self.ackermann_msg.speed          = 2.8
            self.ackermann_msg.steering_angle = delta
            self.ackermann_pub.publish(self.ackermann_msg)

            self.rate.sleep()


def stanley():

    rospy.init_node('stanley_sim_node', anonymous=True)
    sl = Stanley()

    try:
        sl.start_stanley()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    stanley()

