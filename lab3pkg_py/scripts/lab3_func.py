#!/usr/bin/env python
import numpy as np
from lab3_header import *

"""
Translate DH parameters to Homogeneous Transformation (HT) matrix
HT is a 4x4 float numbered numpy 2D array(matrix)
Angles are in radian, distance are in meters.
"""
def DH2HT(a, alpha, d, theta):

	HT = np.zeros((4,4), np.float64)

	##### You code start here #####

	"""
	You will need to write the HT matrix given a, alpha, d and theta
	[ [ ?, ? ,? ,?],
	  [ ?, ? ,? ,?],
	  [ ?, ? ,? ,?],
	  [ ?, ? ,? ,?] ]

	"""

	





	##### You code end here #######


	# Print out a, alpha, d, theta and HT matrix.
	print("a: " + str(a) + ", alpha: " + str(alpha) + \
		  ", d: " + str(d) + ", theta: " + str(theta) + "\n")
	print("HT matrix: \n" + str(HT) + "\n")

	return HT


"""
Function that calculates encoder numbers for each motor
"""
def lab_fk(theta1, theta2, theta3, theta4, theta5, theta6):

	# Initialize the return_value 
	return_value = [None, None, None, None, None, None]

	print("Foward kinematics calculated:\n")

	##### You code start here #####
	# TODO: calculate the homogenous transformation matrix based on the DH table and print result






	"""
	print("DH2HT(?,?,?,?)*" + \
		  "DH2HT(?,?,?,?)*" + \
		  "DH2HT(?,?,?,?)*" + \
		  "DH2HT(?,?,?,?)*" + \
		  "DH2HT(?,?,?,?)*" + \
		  "DH2HT(?,?,?,?)\n")

	"""

	##### You code end here #######

	return_value[0] = theta1 + PI
	return_value[1] = theta2
	return_value[2] = theta3
	return_value[3] = theta4
	return_value[4] = theta5
	return_value[5] = theta6

	return return_value



