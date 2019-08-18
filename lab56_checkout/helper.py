import cv2 

def switch_color(argument):
    switcher = {
        # (blue, green, red)
        0: (0,255,255), 
        1: (255,0,0),   # Blue
        2: (0,255,0),   # Green
        3: (0,0,255),   # Red
        4: (255,255,0), 
        5: (255,0,255),
        6: (128,255,128),
        7: (128,128,0),
        8: (128,0,128),
        9: (0,128,128),
    }
    return switcher.get(argument, (255, 255, 255))

def adaptive_thresholding(gray_image):

    adaptive_threshold_image = cv2.adaptiveThreshold(gray_image.copy(), 
                                        255, 
                                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, #cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, # cv2.THRESH_BINARY_INV
                                        151, 
                                        5)
    #cv2.imshow("Adaptive Threshold Image", adaptive_threshold_image)
    return adaptive_threshold_image

def read_image(image_name):
    image = cv2.imread(image_name, cv2.IMREAD_COLOR)
    height, width = image.shape[0], image.shape[1]
    if(height != 240 and width != 320):
        image = cv2.resize(image, (image.shape[1]/2, image.shape[0]/2)) 
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # print("\nThe shape of the gray image is %s" % str(gray_image.shape))
    return image, gray_image