#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# reads images and does all the magic to generate an input file for the robot

import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy import ndimage as ndi
from skimage import feature
from skimage import io
from skimage import color
from skimage import transform
from skimage import filters
from skimage import util

def openImage(filename):
    # read the image
    filepath = os.getcwd() + '/images/' + filename
    print("Loading image " + filepath)
    im = io.imread(filepath)
    return im

def edgeDetector(imagename):
    im = color.rgb2gray(imagename)  # image is colored, lets make it gray scale
    # edge detection happening here:
#   edges = filters.frangi(im)
    edges = filters.scharr(im)
#   edges = feature.canny(im, sigma=2)
    return edges

def inverter(imagename): # invert image
    inv = util.invert(imagename)
    return inv

def showResults(source, resize, edge, inv): # display results
    print("Drawing images.")
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
            width = size
            height = int(source.shape[1]*size/source.shape[0])
        else:
            width = int(source.shape[0]*size/source.shape[1])
            height = size
        print("Resizing image. original size: " + str(source.shape[0]) + "x" + str(source.shape[1]) + "px. New size: " + str(width) + "x" + str(height) + "px.")
        res = transform.resize(source, (width, height))
        return res

def saveFile(filename, data): # saves result as filename.png in images subfolder
    plt.imsave(os.getcwd() + '/images/' + filename + '.png', data, cmap = plt.cm.gray)

def imageAsArray(filename, threshold): # stores image as binary array, threshold can be set
    image = io.imread(os.getcwd() + '/images/' + filename, as_gray=True)
    for ix in range(image.shape[0]):
        for iy in range(image.shape[1]):
            if np.all(image[ix,iy]) < threshold:
                image[ix,iy] = 0
            else:
                image[ix,iy] = 1
    print("x: " + str(image.shape[0]) + ", y: " + str(image.shape[1]))
    if image.shape[0] < image.shape[1]: # rotate image if height > width
        image = np.rot90(np.rot90(np.rot90(image)))
    print("x: " + str(image.shape[0]) + ", y: " + str(image.shape[1]))
    return image
