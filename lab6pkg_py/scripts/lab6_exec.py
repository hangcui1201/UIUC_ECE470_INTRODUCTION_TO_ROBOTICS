#!/usr/bin/env python

import sys
import copy
import time
import rospy

import numpy as np
from lab6_header import *
from lab6_func import *
from blob_search import *

################################################################################################

# Pre-defined parameters no need to change

# 20Hz
SPIN_RATE = 20 

# UR3 home location
home = [0*PI/180.0, 0*PI/180.0, 0*PI/180.0, 0*PI/180.0, 0*PI/180.0, 0*PI/180.0]

# UR3 current position, using home position for initialization
current_position = copy.deepcopy(home)

thetas = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

digital_in_0 = 0
analog_in_0 = 0.0

suction_on = True
suction_off = False

current_io_0 = False
current_position_set = False

left_click_done = True
right_click_done = True
middle_click_done = True

image_shape_define = False

################################################################################################

# ============================= Student's code starts here ===================================
go_away = [270*PI/180.0, -90*PI/180.0, 90*PI/180.0, -90*PI/180.0, -90*PI/180.0, 130*PI/180.0]
Run_Once = True
xw_yw_R = []
xw_yw_G = []

# Setpoint location (locations for block placement)
setpoints = {} #x_location, y_location, # of stack
setpoints["red"] = [0.16, -0.1, 1]
setpoints["green"] = [0.26, -0.1, 1]

# ============================= Student's code ends here =====================================


"""
Whenever ur3/gripper_input publishes info this callback function is called.
"""
def input_callback(msg):

	global digital_in_0
	global analog_in_0
	digital_in_0 = msg.DIGIN
	digital_in_0 = digital_in_0 & 1 # Only look at least significant bit, meaning index 0
	analog_in_0 = msg.AIN0

"""
Whenever ur3/position publishes info, this callback function is called.
"""
def position_callback(msg):

	global thetas
	global current_position
	global current_position_set

	thetas[0] = msg.position[0]
	thetas[1] = msg.position[1]
	thetas[2] = msg.position[2]
	thetas[3] = msg.position[3]
	thetas[4] = msg.position[4]
	thetas[5] = msg.position[5]

	current_position[0] = thetas[0]
	current_position[1] = thetas[1]
	current_position[2] = thetas[2]
	current_position[3] = thetas[3]
	current_position[4] = thetas[4]
	current_position[5] = thetas[5]

	current_position_set = True

"""
Function to control the suction cup on/off
"""
def gripper(pub_cmd, loop_rate, io_0):

	global SPIN_RATE
	global thetas
	global current_io_0
	global current_position

	error = 0
	spin_count = 0
	at_goal = 0

	current_io_0 = io_0

	driver_msg = command()
	driver_msg.destination = current_position
	driver_msg.v = 1.0
	driver_msg.a = 1.0
	driver_msg.io_0 = io_0  
	pub_cmd.publish(driver_msg)

	while(at_goal == 0):

		if( abs(thetas[0]-driver_msg.destination[0]) < 0.0005 and \
			abs(thetas[1]-driver_msg.destination[1]) < 0.0005 and \
			abs(thetas[2]-driver_msg.destination[2]) < 0.0005 and \
			abs(thetas[3]-driver_msg.destination[3]) < 0.0005 and \
			abs(thetas[4]-driver_msg.destination[4]) < 0.0005 and \
			abs(thetas[5]-driver_msg.destination[5]) < 0.0005 ):

			#rospy.loginfo("Goal is reached!")
			at_goal = 1
		
		loop_rate.sleep()

		if(spin_count >  SPIN_RATE*5):

			pub_cmd.publish(driver_msg)
			rospy.loginfo("Just published again driver_msg")
			spin_count = 0

		spin_count = spin_count + 1

	return error

"""
Move robot arm from one position to another
"""
def move_arm(pub_cmd, loop_rate, dest, vel, accel):

	global thetas
	global SPIN_RATE

	error = 0
	spin_count = 0
	at_goal = 0

	driver_msg = command()
	driver_msg.destination = dest
	driver_msg.v = vel
	driver_msg.a = accel
	driver_msg.io_0 = current_io_0
	pub_cmd.publish(driver_msg)

	loop_rate.sleep()

	while(at_goal == 0):

		if( abs(thetas[0]-driver_msg.destination[0]) < 0.0005 and \
			abs(thetas[1]-driver_msg.destination[1]) < 0.0005 and \
			abs(thetas[2]-driver_msg.destination[2]) < 0.0005 and \
			abs(thetas[3]-driver_msg.destination[3]) < 0.0005 and \
			abs(thetas[4]-driver_msg.destination[4]) < 0.0005 and \
			abs(thetas[5]-driver_msg.destination[5]) < 0.0005 ):

			at_goal = 1
			#rospy.loginfo("Goal is reached!")
		
		loop_rate.sleep()

		if(spin_count >  SPIN_RATE*5):

			pub_cmd.publish(driver_msg)
			rospy.loginfo("Just published again driver_msg")
			spin_count = 0

		spin_count = spin_count + 1

	return error


# ============================= Student's code starts here ===================================
def move_block(pub_cmd, loop_rate, xw_yw, setpoint, vel, accel):
	# Calling inverse kinematic
	target = lab_invk(xw_yw[0], xw_yw[1], 0.02+0.014, 60)
	target_air = lab_invk(xw_yw[0], xw_yw[1], 0.02+(4*0.014), 60)
	mid_air = lab_invk(0.25, 0.2, 0.15, 60)
	place = lab_invk(setpoint[0] , setpoint[1], 0.02+(setpoint[2]*0.015), 60)
	place_air = lab_invk(setpoint[0] , setpoint[1], 0.02+((setpoint[2]+4)*0.015), 60)

	vel = 4.0
	accel = 4.0
	error = 0

	print("moving........")
	
	#move_arm(pub_cmd, loop_rate, mid_air, vel, accel)
	# Send arm to target location
	move_arm(pub_cmd, loop_rate, target_air, vel, accel)
	move_arm(pub_cmd, loop_rate, target, vel, accel)

	# Active gripper
	gripper(pub_cmd, loop_rate, suction_on)
	time.sleep(1.0)
	if(digital_in_0 == 0):
		gripper(pub_cmd, loop_rate, suction_off)
		time.sleep(0.2) # Shutdown suction cup
		move_arm(pub_cmd, loop_rate, go_away, vel, accel)
		error = 1
		return error

	# Send arm to mid_air location to avoid obstacle
	move_arm(pub_cmd, loop_rate, target_air, vel, accel)

	# Send arm to place location
	move_arm(pub_cmd, loop_rate, place_air, vel, accel)
	move_arm(pub_cmd, loop_rate, place, vel, accel)

	# Deactive gripper
	if(digital_in_0 == 1):
		gripper(pub_cmd, loop_rate, suction_off)
		time.sleep(0.2)

	# Send arm to mid_air location to standby
	move_arm(pub_cmd, loop_rate, place_air, vel, accel)

	return error
# ============================= Student's code ends here =====================================

class ImageConverter:

    def __init__(self, SPIN_RATE):

        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher("/image_converter/output_video", Image, queue_size=10)
        self.image_sub = rospy.Subscriber("/cv_camera_node/image_raw", Image, self.image_callback)
        self.coord_pub = rospy.Publisher("/coord_center", String, queue_size=10)
        self.loop_rate = rospy.Rate(SPIN_RATE)

        # Check if ROS is ready for operation
        while(rospy.is_shutdown()):
        	print("ROS is shutdown!")


    def image_callback(self, data):

# ============================= Student's code starts here ===================================
		# Calling global variables
        global xw_yw_R
        global xw_yw_G
        global Run_Once
# ============================= Student's code ends here =====================================

        try:
		  # Convert ROS image to OpenCV image
            raw_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        cv_image = cv2.flip(raw_image, -1)
        cv2.line(cv_image, (0,50), (640,50), (0,0,0), 5)

# ============================= Student's code starts here ===================================

		# Run blob_search until at least one block per each color is found
        if Run_Once is True:
        	target_color = "red"
        	xw_yw_R = blob_search(cv_image, target_color)
        	if len(xw_yw_R) >0:
        		target_color = "green"
        		xw_yw_G = blob_search(cv_image, target_color)
        		if len(xw_yw_G) >0:
        			Run_Once = False
    			else:
        			print("no green block!")
        	else:
        		print("no red block!")
# ============================= Student's code ends here =====================================

        try:
		  # Convert OpenCV image to ROS image and publish
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
        except CvBridgeError as e:
            print(e)



"""
Program run from here
"""
def main():
# ============================= Student's code starts here ===================================
	# Calling global variables
	global target_color
	global target_spot
	global Run_Once
# ============================= Student's code ends here =====================================

	# Initialize ROS node
	rospy.init_node('lab6node')

    # Initialize publisher for ur3/command with buffer size of 10
	pub_command = rospy.Publisher('ur3/command', command, queue_size=10)

	# Initialize subscriber to ur3/position & ur3/gripper_input and callback fuction
	# each time data is published
	sub_position = rospy.Subscriber('ur3/position', position, position_callback)
	sub_input = rospy.Subscriber('ur3/gripper_input', gripper_input, input_callback)

	# Check if ROS is ready for operation
	while(rospy.is_shutdown()):
		print("ROS is shutdown!")

	# Initialize the rate to publish to ur3/command
	loop_rate = rospy.Rate(SPIN_RATE)

	vel = 4.0
	accel = 4.0
	move_arm(pub_command, loop_rate, go_away, vel, accel)

	ic = ImageConverter(SPIN_RATE)
	time.sleep(1)

# ============================= Student's code starts here ===================================
	# Capture the block locations found by blob_search
	redBlocks = np.array(xw_yw_R)
	greenBlocks = np.array(xw_yw_G)

	# Pick and Place the red blocks
	if len(redBlocks) > 0:
		print("number of red blocks: ")
		print(len(redBlocks))

		target_spot = setpoints["red"]
		for i in range(len(redBlocks)):
			move_block(pub_command, loop_rate, redBlocks[i], target_spot, vel, accel)
			target_spot[2] += 2
			print("trial finished!")
	
	# Pick and Place the green blocks
	if len(greenBlocks) > 0:
		print("number of green blocks: ")
		print(len(greenBlocks))

		target_spot = setpoints["green"]
		for i in range(len(greenBlocks)):
			move_block(pub_command, loop_rate, greenBlocks[i], target_spot, vel, accel)
			target_spot[2] += 2
			print("trial finished!")

	move_arm(pub_command, loop_rate, go_away, vel, accel)
# ============================= Student's code ends here =====================================

	rospy.loginfo("-= Task Completed =-")
	print("Use Ctrl+C to exit program")
	rospy.spin()

if __name__ == '__main__':
	
	try:
		main()
    # When Ctrl+C is executed, it catches the exception
	except rospy.ROSInterruptException:
		pass
