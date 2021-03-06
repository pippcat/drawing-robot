#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import logging
import warnings
import numpy as np
import matplotlib.pyplot as plt
from skimage import io
from skimage import color
from skimage import filters
from skimage import feature
from skimage import transform
from PIL import Image


def open_image(filename):
    '''
    Opens an image and returns it.

    It also rotates it to landscape if it is a portrait image.

    :param filename: file name
    :returns: image
    '''

    filepath = os.getcwd()+ '/drawing-robot/static/' + filename
    logging.info("Loading image " + filepath)
    im = io.imread(filepath)
    if im.shape[0] < im.shape[1]: # rotate image if height > width
        im = np.rot90(im)
    return im

def detect_edges(imagename, algorithm):
    '''
    Does edge detection by the choosen algorithm.

    :param imagename: image name
    :param algorithm: has to be "roberts", "scharr", "prewitt", "canny-1", "canny-2" or "canny3"
    :returns: image
    '''

    im = color.rgb2gray(imagename)  # image is colored, lets make it gray scale
    logging.info(algorithm + ' was choosen as edge detection algorithm.')
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
    '''
    Inverts an image and returns it.
    :param imagename: image name
    :returns: image
    '''

    logging.info('Inverting image.')
    inv = 1 - np.asarray(imagename)
    return inv

def resize_image(source, size):
    '''
    Resizes an image to the given size and returns it.

    It also rotates portrait images to landscape images first.abs

    :param source: image source
    :param size: size to which long size should be set
    :returns: image
    '''

    # transform throws warnings which we'd like to supress, therefore:
    logging.info('Resizing image.')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        '''longer side of image will be set to size, other one is calculated
        to keep aspect ratio constant'''
        if source.shape[0] > source.shape[1]:
            logging.info("Image is in landscape format.")
            width = size
            height = int(source.shape[1]*size/source.shape[0])
        else:
            logging.info("Image is in portrait format.")
            width = int(source.shape[0]*size/source.shape[1])
            height = size
        logging.info("Resizing image. original size: " + str(source.shape[0]) + "x" + str(source.shape[1]) + "px. New size: " + str(width) + "x" + str(height) + "px.")
        res = transform.resize(source, (width, height))
        return res

def save_file(filename, data):
    '''
    Saves result as filename.png in images subfolder.

    :param filename: name of file in drawing-robot/static/ folder
    :param data: image
    '''

    logging.info('Saving file as ' + filename)
    if data.shape[0] > data.shape[1]: # rotate image if height > width
        data = np.rot90(data)
    plt.imsave(os.getcwd()+ '/drawing-robot/static/' + filename, data, cmap = plt.cm.gray)

def image_as_array(filename, threshold):
    '''
    Stores image as binary array, threshold can be set.

    :param filename: file name
    :param threshold: threshold for conversion, has to be between 0 and 1
    :returns: image as array
    '''

    logging.info('Converting image to array')
    print(filename)
    imagefile = Image.open('drawing-robot/static/' + filename).convert("L") # open image and convert to grayscale
    imageAsArray = np.asarray(imagefile)
    imageAsArray.setflags(write=1) # it's read only by default
    for ix in range(imageAsArray.shape[0]):
        for iy in range(imageAsArray.shape[1]):
            if imageAsArray[ix,iy] < threshold*255: # treshold 0 .. 1 , array 0 .. 255
                imageAsArray[ix,iy] = 0
            else:
                imageAsArray[ix,iy] = 1
    if imageAsArray.shape[0] < imageAsArray.shape[1]: # rotate image if height > width
        imageAsArray = np.rot90(imageAsArray, k=3)
    return imageAsArray
