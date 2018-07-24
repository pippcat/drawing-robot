#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage import feature
from skimage import io
from skimage import color

def edge_detector(filename, sigma):

    # read the image
    filepath = os.getcwd() + '/images/' + filename
    im = io.imread(filepath)

    # image is colored, lets make it gray scale
    im = color.rgb2gray(im)

    # Compute the Canny filter for two values of sigma
    edges = feature.canny(im, sigma=sigma)

    # display results
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 3),
                                                sharex=True, sharey=True)

    ax1.imshow(im, cmap=plt.cm.gray)
    ax1.axis('off')
    ax1.set_title('source image in grayscale', fontsize=20)

    ax2.imshow(edges, cmap=plt.cm.gray)
    ax2.axis('off')
    ax2.set_title('Canny filter, $\sigma=$' + str(sigma), fontsize=20)

    fig.tight_layout()

    plt.show()
