#!/usr/bin/env python

import numpy as np 

def switch_color(argument):
    switcher = {
        # (blue, green, red)
        0: (255,255,255),
        1: (255,0,0),
        2: (0,255,0),
        3: (0,0,255),
        4: (255,255,0),
        5: (255,0,255),
        6: (0,255,255),
        7: (128,128,0),
        8: (128,0,128),
        9: (0,128,128),
    }
    return switcher.get(argument, (0,0,0))
    

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