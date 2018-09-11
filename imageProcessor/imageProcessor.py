#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# reads images and does all the magic to generate an input file for the robot

import os
import numpy as np
np.set_printoptions(threshold=np.nan)
import matplotlib.pyplot as plt
import warnings
from PIL import Image
import PIL.ImageOps
from scipy import ndimage as ndi
from skimage import feature
from skimage import io
from skimage import color
from skimage import transform
from skimage import filters
from skimage import util


image = {}
def openImage(filename):
    # read the image
    print(os.getcwd()+ '/drawing-robot/static/' + filename)
    filepath = os.getcwd()+ '/drawing-robot/static/' + filename
    print("Loading image " + filepath)
    im = io.imread(filepath)
    if im.shape[0] < im.shape[1]: # rotate image if height > width
        im = np.rot90(im)
    return im

def edgeDetector(imagename, algorithm):
    im = color.rgb2gray(imagename)  # image is colored, lets make it gray scale
    print('algorithm',algorithm)
    if algorithm == "frangi":
        edges = filters.frangi(im)
    elif algorithm == "scharr":
        edges = filters.scharr(im)
    elif algorithm == "canny":
        edges = feature.canny(im, sigma=2)
    return edges

def inverter(imagename): # invert image
    inv = 1 - np.asarray(imagename)
#inv = PIL.ImageOps.invert(imagename)
    return inv
#    return imagename

def showResults(source, resize, edge, inv): # display results
    fig, axes = plt.subplots(nrows=2, ncols=2)

    ax = axes.ravel()
    ax[0].imshow(source, cmap=plt.cm.gray)
    ax[0].set_title('source image', fontsize=20)

    ax[1].imshow(resize, cmap=plt.cm.gray)
    ax[1].set_title('resized image', fontsize=20)

    ax[2].imshow(edge, cmap=plt.cm.gray)
    ax[2].set_title('edge detection', fontsize=20)

    ax[3].imshow(inv, cmap=plt.cm.gray)
    ax[3].set_title('inversed result', fontsize=20)

    fig.tight_layout()

    plt.show()

def resizeImage(source, size):
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

def saveFile(filename, data): # saves result as filename.png in images subfolder
    if data.shape[0] > data.shape[1]: # rotate image if height > width
        data = np.rot90(data)
    plt.imsave(os.getcwd()+ '/drawing-robot/static/' + filename, data, cmap = plt.cm.gray)

def imageAsArray(filename, threshold): # stores image as binary array, threshold can be set
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
    # adding a border to the image to circumvent problems with pixel finding algorithm:
#    imageAsArray = np.pad(imageAsArray, pad_width=2, mode='constant', constant_values=1)
    #print("made array of size x: " + str(imageAsArray.shape[0]) + ", y: " + str(imageAsArray.shape[1]))
    return imageAsArray
