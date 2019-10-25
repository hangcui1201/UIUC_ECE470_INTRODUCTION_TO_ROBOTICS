#!/usr/bin/env python
import numpy as np
from scipy.linalg import expm
from lab5_header import *

"""
Use 'expm' for matrix exponential.
Angles are in radian, distance are in meters.
"""
def Get_MS():
	# =================== Your code starts here ====================#
	# Fill in the correct values for a1~6 and q1~6, as well as the M matrix
	M = np.eye(4)
	S = np.zeros((6,6))




	
	# ==============================================================#
	return M, S


"""
Function that calculates encoder numbers for each motor
"""
def lab_fk(theta1, theta2, theta3, theta4, theta5, theta6):

	# Initialize the return_value 
	return_value = [None, None, None, None, None, None]

	print("Foward kinematics calculated:\n")

	# =================== Your code starts here ====================#
	theta = np.array([theta1,theta2,theta3,theta4,theta5,theta6])
	T = np.eye(4)

	M, S = Get_MS()








	# ==============================================================#
	
	print(str(T) + "\n")

	return_value[0] = theta1 + PI
	return_value[1] = theta2
	return_value[2] = theta3
	return_value[3] = theta4 - (0.5*PI)
	return_value[4] = theta5
	return_value[5] = theta6

	return return_value


"""
Function that calculates an elbow up Inverse Kinematic solution for the UR3
"""
def lab_invk(xWgrip, yWgrip, zWgrip, yaw_WgripDegree):

    # theta1 to theta6
	thetas = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

	a1 = 0
	d1 = 0.152
	a2 = 0.244
	d2 = 0.120
	a3 = 0.213
	d3 = -0.093
	a4 = 0
	d4 = 0.083
	a5 = 0
	d5 = 0.083
	a6 = 0.0535
	d6 = (0.082+0.056)

	# xgrip = ?
	# ygrip = ?
	# zgrip = ?

	# xcen = ?
	# ycen = ?
	# zcen = ?

	# theta1
	thetas[0] = 0        # Default value Need to Change

	# theta6
	thetas[5] = PI/2     # Default value Need to Change
 
	# x3end = ?
	# y3end = ?
	# z3end = ?

	thetas[1]= -PI/4     # Default value Need to Change
	thetas[2]= PI/2      # Default value Need to Change
	thetas[3]= (-PI*3)/4 # Default value Need to Change
	thetas[4]=-PI/2      # Default value Need to Change

	print("theta1 to theta6: " + str(thetas) + "\n")

	return lab_fk(float(thetas[0]), float(thetas[1]), float(thetas[2]), \
		          float(thetas[3]), float(thetas[4]), float(thetas[5]) )