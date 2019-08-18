#!/usr/bin/env python

import sys
import cv2
import copy
import numpy as np 

import rospy
import roslib
import rospkg

from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge, CvBridgeError

# messages for student to use
from ur3_driver.msg import command
from ur3_driver.msg import position
from ur3_driver.msg import gripper_input

from helper import *
from lab5_func import associate_objects
from lab5_func_fast import associate_objects_fast
from lab5_func_fast_soln import associate_objects_fast_soln

################################################

# Change this value to 0, 1 or 2
switch_to_cython = 0

# Params for lab6
beta = None
theta = None
tx = None
ty = None

xw = np.zeros(30, dtype = np.float64)
yw = np.zeros(30, dtype = np.float64)

################################################

# Pre-defined parameters no need to change

PI = 3.14159265

SPIN_RATE = 20 # 20Hz

digital_in_0 = 0
analog_in_0 = 0.0

suction_on = True
suction_off = False

current_io_0 = False
current_position_set = False

thetas = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
home = [180*PI/180.0, -90*PI/180.0, 90*PI/180.0, -90*PI/180.0, -90*PI/180.0, 0*PI/180.0]
current_position = copy.deepcopy(home)

left_click_done = True
right_click_done = True
middle_click_done = True

image_shape_define = False


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


# def on_mouse(event, x, y, flags, userdata):
#     pass

class ImageConverter:

    def __init__(self, SPIN_RATE):

        self.bridge = CvBridge()

        self.image_pub = rospy.Publisher("/image_converter/output_video", Image, queue_size=10)
        self.image_sub = rospy.Subscriber("/cv_camera_node/image_raw", Image, self.image_callback)
        #cv2.namedWindow(OPENCV_WINDOW, cv2.WINDOW_NORMAL)
        #cv2.namedWindow(OPENCV_WINDOW)

        self.pub_command = rospy.Publisher('ur3/command', command, queue_size=10)
        self.sub_position = rospy.Subscriber('ur3/position', position, self.position_callback)
        self.sub_input = rospy.Subscriber('ur3/gripper_input', gripper_input, self.input_callback)

        # Check if ROS is ready for operation
        while(rospy.is_shutdown()):
        	print("ROS is shutdown!")

        loop_rate = rospy.Rate(SPIN_RATE)

        move_arm(self.pub_command, loop_rate, lab_invk(0.1, -0.3, 0.2, -90), 4.0, 4.0)

    """
    Whenever ur3/danposition publishes info, this callback function is called.
    """
    def position_callback(self, msg):

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
    Whenever ur3/daninput publishes info this callback function is called.
    """
    def input_callback(self, msg):
        global digital_in_0
        global analog_in_0
        digital_in_0 = msg.DIGIN
        digital_in_0 = digital_in_0 & 1 # Only look at least significant bit, meaning index 0
        analog_in_0 = msg.AIN0


    def image_callback(self, data):

        global switch_to_cython
        global image_shape_define

        try:
            # Convert ROS image to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        # Create a gray scale image
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        #print("The image size is " + str(gray_image.shape))

        # Create a binary image
        binary_image = cv2.adaptiveThreshold(gray_image, 
                                            255, 
                                            cv2.ADAPTIVE_THRESH_MEAN_C, 
                                            cv2.THRESH_BINARY, 131, 12)

        if(image_shape_define == False):
            self.height = binary_image.shape[0]
            self.width = binary_image.shape[1]
        else:
            image_shape_define = True

        # Create a 2D array pixellabel[height][width]
        # In the bw_image, 0 is black, 255 is white
        # If image pixel is white pixellabel[row][col] = -1
        # If image pixel is black pixellabel[row][col] = 0
        pixellabel = ((binary_image.copy()+1)*-1+1)*-1 # np.int16 == short

        # Assign unique color to each object
        associate_image = np.zeros([self.height, self.width, 3], dtype=np.uint8)

        label = np.zeros(20000, dtype=np.uint16)
        equiv = np.arange(20000, dtype=np.uint16)
        object_num = np.zeros(20000, dtype=np.uint16)
        object_label = np.zeros(self.block_num, dtype=np.int32) # assume there are at most 30 blocks

        object_row = np.zeros(self.block_num, dtype = np.int32)
        object_col = np.zeros(self.block_num, dtype = np.int32)
        object_image = np.zeros(self.block_num, dtype = np.int32)
        object_image_row = np.zeros(self.block_num, dtype = np.int32)
        object_image_col = np.zeros(self.block_num, dtype = np.int32)

        if (switch_to_cython == 0):
            # Get associate image
            start_time = time.time()
            binary_image = cv2.resize(binary_image, (binary_image.shape[1]/2, binary_image.shape[0]/2))
            pixellabel = ((binary_image.copy()+1)*-1+1)*-1   # np.int16 == short
            associate_image = np.zeros([self.height/2, self.width/2, 3], dtype=np.uint8)
            associate_image = associate_objects(binary_image.copy(), pixellabel, associate_image)
            print("Associate objects without Cython processed %s seconds." % (time.time() - start_time))
        elif(switch_to_cython == 1):
            # Get associate image
            start_time = time.time()
            associate_image = associate_objects_fast(binary_image.copy(), pixellabel, associate_image)
            associate_image = np.asarray(associate_image)
            print("Associate objects with Cython for demo processed %s seconds." % (time.time() - start_time))
        elif(switch_to_cython == 2):
            # Get associate image
            start_time = time.time()
            associate_image = associate_objects_fast_soln(binary_image.copy(), pixellabel, associate_image, label,
                                                          equiv, object_num, object_label, object_row, object_col,
                                                          object_image, object_image_row, object_image_col)
            associate_image = np.asarray(associate_image)
            print("Associate objects with Cython for Lab5 Solution processed %s seconds." % (time.time() - start_time))
        else:
            print("Wrong switch_to_cython value.")

        cv2.namedWindow("Image Window")
        # cv2.namedWindow("Grayscale Image")
        cv2.namedWindow("Binary Image")
        cv2.namedWindow("Associate Objects")

        cv2.setMouseCallback("Image Window", self.on_click)
        # cv2.setMouseCallback("Grayscale Image", self.on_click)
        cv2.setMouseCallback("Binary Image", self.on_click)
        cv2.setMouseCallback("Associate Objects", self.on_click)

        cv2.imshow("Image Window", cv_image)
        # cv2.imshow("Grayscale Image", gray_image)
        cv2.imshow("Binary Image", binary_image)
        cv2.imshow("Associate Objects", associate_image)

        cv2.waitKey(3)

        try:
            # Convert OpenCV image to ROS image and publish
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
        except CvBridgeError as e:
            print(e)


    """
    Function for Lab 6

    This is a call back function of mouse click, it will be called when there's a click on the video window.
    You will write your coordinate transformation in on_click function.

    By calling on_click, you can use the variables calculated in the class function directly and use publisher
    initialized in constructor to control the robot.

    Lab4 and Lab3 functions can be used since they are imported from helper.py 
    """
    def on_click(self, event, x, y, flags, param):

        global left_click_done
        global right_click_done
        global middle_click_done

        # For use with Lab 6
        # If the robot is holding a block, place it at the designated row and column. 
        if (event == cv2.EVENT_LBUTTONDOWN):

            if (left_click_done == True):

                left_click_done = False  # Code started
                print("left click: (" + str(x) + ", " + str(y) + ")")

                ###### Put your left click code here






                ###### Put your left click code here

                left_click_done = True  # Code finished
            else:
                print("Previous left click is not finished, ignoring this click!")

        elif (event == cv2.EVENT_MBUTTONDOWN): # MBUTTONDOWN

            if (middle_click_done == True):
                
                middle_click_done = False  # Code started
                print("middle click: (" + str(x) + ", " + str(y) + ")")

                ###### Put your middle click code here






                ###### Put your middle click code here

                middle_click_done = True  # Code finished
            else:
                print("Previous middle click is not finished, ignoring this click!")
        else:
            pass



def main():

    global SPIN_RATE

    rospy.init_node('lab56node', anonymous=True)

    ic = ImageConverter(SPIN_RATE)

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down!")

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
