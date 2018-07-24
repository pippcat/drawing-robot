#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage import feature
from skimage import io
from skimage import color
from skimage import transform
from skimage import filters
from skimage import util

def open_image(filename):
    # read the image
    filepath = os.getcwd() + '/images/' + filename
    im = io.imread(filepath)
    return im

def edge_detector(imagename):

    # image is colored, lets make it gray scale
    im = color.rgb2gray(imagename)

    # Compute the Canny filter for two values of sigma
#   edges = filters.frangi(im)
    edges = filters.scharr(im)
#    edges = feature.canny(im, sigma=sigma)
    return edges

def inverter(imagename):
    inv = util.invert(imagename)
    return inv

def show_results(source, resize, edge, inv):
    # display results
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

def resize_image(source, sizex):
    print(source.shape)
    print(sizex, int(source.shape[1]*sizex/source.shape[0]))
    res = transform.resize(source, (sizex,int(source.shape[1]*sizex/source.shape[0])))
    return res

