#!/usr/bin/env python3
#-*- coding: utf-8 -*-

def open_image(filename):
    '''Opens an image and returns it.'''

    import os
    import numpy as np
    from skimage import io

    print(os.getcwd()+ '/drawing-robot/static/' + filename)
    filepath = os.getcwd()+ '/drawing-robot/static/' + filename
    print("Loading image " + filepath)
    im = io.imread(filepath)
    if im.shape[0] < im.shape[1]: # rotate image if height > width
        im = np.rot90(im)
    return im

def detect_edges(imagename, algorithm):
    '''Does edge detection by the choosen algorithm.

    Valid algorithms:
        - roberts
        - scharr
        - sobel
        - prewitt
        - canny-1
        - canny-2
        - canny-3'''

    from skimage import color
    from skimage import filters
    from skimage import feature

    im = color.rgb2gray(imagename)  # image is colored, lets make it gray scale
    print('algorithm',algorithm)
    if algorithm == "roberts":
        edges = filters.roberts(im)
    elif algorithm == "scharr":
        edges = filters.scharr(im)
    elif algorithm == "sobel":
        edges = filters.sobel(im)
    elif algorithm == "prewitt":
        edges = filters.prewitt(im)
    elif algorithm == "canny-1":
        edges = feature.canny(im, sigma=1)
    elif algorithm == "canny-2":
        edges = feature.canny(im, sigma=2)
    elif algorithm == "canny-3":
        edges = feature.canny(im, sigma=3)
    return edges

def invert_images(imagename):
    '''Inverts an image and returns it.'''

    import numpy as np

    inv = 1 - np.asarray(imagename)
    return inv

def resize_image(source, size):
    '''Resizes an image to the given size and returns it.'''

    from skimage import transform
    import warnings

    # transform throws warnings which we'd like to supress, therefore:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if source.shape[0] > source.shape[1]: # longer side of image will be set to size, other one is calculated to keep aspect ratio constant
            print("landscape")
            width = size
            height = int(source.shape[1]*size/source.shape[0])
        else:
            print("portrait")
            width = int(source.shape[0]*size/source.shape[1])
            height = size
        print("Resizing image. original size: " + str(source.shape[0]) + "x" + str(source.shape[1]) + "px. New size: " + str(width) + "x" + str(height) + "px.")
        res = transform.resize(source, (width, height))
        return res

def save_file(filename, data):
    '''Saves result as filename.png in images subfolder.'''

    import numpy as np
    import matplotlib.pyplot as plt
    import os

    if data.shape[0] > data.shape[1]: # rotate image if height > width
        data = np.rot90(data)
    plt.imsave(os.getcwd()+ '/drawing-robot/static/' + filename, data, cmap = plt.cm.gray)

def image_as_array(filename, threshold):
    '''Stores image as binary array, threshold can be set.'''

    import numpy as np
    import os
    from PIL import Image

    imagefile = Image.open(os.getcwd()+ '/drawing-robot/static/' + filename).convert("L") # open image and convert to grayscale
    imageAsArray = np.asarray(imagefile)
    imageAsArray.setflags(write=1) # it's read only by default
    for ix in range(imageAsArray.shape[0]):
        for iy in range(imageAsArray.shape[1]):
            if imageAsArray[ix,iy] < threshold*255: # treshold 0 .. 1 , array 0 .. 255
                imageAsArray[ix,iy] = 0
            else:
                imageAsArray[ix,iy] = 1
    if imageAsArray.shape[0] < imageAsArray.shape[1]: # rotate image if height > width
        imageAsArray = np.rot90(imageAsArray)
    return imageAsArray
