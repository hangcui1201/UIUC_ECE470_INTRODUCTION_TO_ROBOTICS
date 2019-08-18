#!/usr/bin/env python

import cv2
import time
import numpy as np
from helper import switch_color, read_image, adaptive_thresholding

# Function for Lab 5
# Take an black and white image and find the object in it, returns an associated image with different color for each image
# You will implement your algorithm for rastering here
def associate_objects(bw_image, pixellabel, associate_image):

    height, width = bw_image.shape[0], bw_image.shape[1]
    
    # Create a demo image of colored lines
    num = 0  
    for row in range(height):
        for col in range(width):
            pixellabel[row][col] = num
        num = num + 1
        if(num == 10):
            num = 0        

    for row in range(height):
        for col in range(width):
            (blue, green, red) = switch_color(pixellabel[row][col])
            associate_image[row][col][0] = blue
            associate_image[row][col][1] = green
            associate_image[row][col][2] = red

    return associate_image


if __name__ == '__main__':

    image_name = "./images/1.jpg"
    image, gray_image = read_image(image_name)
    bw_image = adaptive_thresholding(gray_image)

    height, width = bw_image.shape[0], bw_image.shape[1]
    
    # Create a 2D array pixellabel[height][width]
    # In the bw_image, 0 is black, 255 is white
    # If image pixel is white pixellabel[row][col] = -1
    # If image pixel is black pixellabel[row][col] = 0
    # pixellabel = ((bw_image.copy()+1)*-1+1)*-1
    pixellabel = ((bw_image.copy()+1)*-1+1)*-1 # numpy.int16 == short
    
    associate_image = np.zeros([height, width, 3], dtype=np.uint8)

    start_time = time.time()
    result_image = associate_objects(bw_image, pixellabel, associate_image)
    end_time = time.time()
    print("Associate objects without Cython processed %s seconds." % (end_time - start_time))

    cv2.imshow("(1) Original Image", image)
    cv2.imshow("(2) Gray Image", gray_image)
    cv2.imshow("(3) Binary Image", bw_image)
    cv2.imshow("(4) Result Image", result_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

