#!/usr/bin/env python

import cv2
import numpy as np

# ============================= Student's code starts here ===================================
# Params for camera calibration
theta = 0 
beta = 740.0
tx = -0.282094594595
ty = -0.143581081081

# HSV color space H:0-179, S:0-255, V:0-255
color_space = {}
color_space["red"] = np.array([[0,200,60],[3,255,120]])
color_space["green"] = np.array([[51,0,0],[71,255,232]])

# Function that converts image coord to world coord
def IMG2W(x,y):
    xw_cal = (((y-240)/beta - tx) * np.cos(theta) + ((x-320)/beta - ty) * np.sin(theta)) - 0.005
    yw_cal = ((y-240)/(beta) - tx) * -np.sin(theta) + ((x-320)/(beta) - ty) * np.cos(theta) + 0.008
    return xw_cal, yw_cal
# ============================= Student's code ends here =====================================

def blob_search(image_raw, color):
	
# ============================= Student's code starts here ===================================
	# What color are we picking?
	target_color = color_space[color]
	color_l = target_color[0]
	color_h = target_color[1]

	# Crop the image to focus on the center only
	image = image_raw[100:330, 100:540].copy()
# ============================= Student's code ends here =====================================

	# Convert the image into the HSV color space
	hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	# Define a mask using the lower and upper bounds of the target color 
	mask_image = cv2.inRange(hsv_image, color_l, color_h)

	# Setup SimpleBlobDetector parameters.
	params = cv2.SimpleBlobDetector_Params()

	params.minDistBetweenBlobs = 20.0

	# Filter by Color 
	params.filterByColor = False

	# Filter by Area.
	params.filterByArea = True
	params.minArea = 300          
	params.maxArea = 1400        

	# Filter by Circularity
	params.filterByCircularity = False
	params.filterByInertia = False
	params.filterByConvexity = False

	# Create a detector with the parameters
	detector = cv2.SimpleBlobDetector_create(params)

	# Detect blobs.
	keypoints = detector.detect(mask_image)

	im_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

	blob_image_center = []

	for i in keypoints:
		# Get center of the image
		im_with_keypoints = cv2.circle(im_with_keypoints, (int(i.pt[0]), int(i.pt[1])), 2, (0, 255, 0), -1)
		xy_center = [int(i.pt[0]+100), int(i.pt[1]+100)] # Remember to add the offset caused by cropping!!!!!
		blob_image_center.append(xy_center)

# ============================= Student's code starts here ===================================
	xw_yw = []

	if(len(blob_image_center) == 0):
		print("No block found!")
	else:
		for i in range(len(blob_image_center)):
		    x = blob_image_center[i][0]
		    y = blob_image_center[i][1]
		    xw_block, yw_block = IMG2W(x,y)
		    xw_yw.append([xw_block, yw_block])
# ============================= Student's code ends here =====================================

	cv2.namedWindow("Camera View")
	cv2.imshow("Camera View", im_with_keypoints)

	cv2.waitKey(2)

	return xw_yw