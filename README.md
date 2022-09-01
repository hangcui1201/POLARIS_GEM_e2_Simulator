### Polaris GEM e2 Simulator

#### System: Ubuntu 20.04 + ROS Noetic (Gazebo 11)

#### Author: Hang Cui (hangcui1201@gmail.com)

This simulator was initially developed with ROS Melodic and Gazebo 9 in Ubuntu 18.04 for personal research in fall 2019. The Polaris GEM e2 vehicle was measured and modeled by Hang Cui and Jiaming Zhang using Solidworks. The compatible URDF files of simulator for RViz and Gazebo were constructed by Hang Cui. Later, this project was funded by the [Center of Autonomy](https://autonomy.illinois.edu/) at University of Illinois at Urbana-Champaign. It was further developed and merged into ROS Noetic and Gazeno 11 in the summer of 2021. This simulator is currently under development for research and teaching at University of Illinois at Urbana-Champaign.  

#### Simple Track Environment

$ source devel/setup.bash  
$ roslaunch gem_gazebo gem_gazebo_rviz.launch velodyne_points:="true"

<a href="url"><img src="./images/simple_track_rviz.png" width="600"></a>  

<a href="url"><img src="./images/simple_track_gazebo.png" width="600"></a>  


#### Geometric based Lateral Controller

$ source devel/setup.bash  
$ roslaunch gem_gazebo gem_gazebo_rviz.launch  

$ source devel/setup.bash  
$ roslaunch gem_gazebo gem_sensor_info.launch  

$ source devel/setup.bash  
$ rosrun gem_pure_pursuit_sim pure_pursuit_sim.py

<a href="url"><img src="./images/pp_controller.gif" width="600"></a>  

$ source devel/setup.bash  
$ rosrun gem_stanley_sim stanley_sim.py  

<a href="url"><img src="./images/stanley_controller_rviz.gif" width="600"></a>  

<a href="url"><img src="./images/stanley_controller_gazebo.gif" width="600"></a>  


#### Highbay Environment

$ source devel/setup.bash  
$ roslaunch gem_gazebo gem_gazebo_rviz.launch world_name:="highbay_track.world" x:=-5.5 y:=-21 velodyne_points:="true"
  
$ source devel/setup.bash  
$ roslaunch gem_gazebo gem_sensor_info.launch

<a href="url"><img src="./images/highbay_rviz.png" width="600"></a>  

<a href="url"><img src="./images/highbay_gazebo.png" width="600"></a>  