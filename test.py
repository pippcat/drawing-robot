#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from imageProcessor.imageProcessor import *
import string
from random import choice
import os
from bokeh.models import ColumnDataSource

def randomChar(y):
    return ''.join(choice(string.ascii_letters) for x in range(y))

def tester():
    image['inputFilename'] = 'sxIJJhLq_orig.png'
    image['outputSize'] = 200
    image['edgeAlgorithm'] = 'scharr' # value is a list containing one item
    image['treshold'] = 0.8
    #save settings before!
    imagename = randomChar(8)
    print('Image name on hard disk:',imagename)
    im = openImage(image['inputFilename']) # open image
    saveFile(imagename + '_orig.png', im)
    print('im')
    res = resizeImage(im,image['outputSize']) # resize it
    saveFile(imagename + '_scaledown.png', res)
    print('res')
    edge = edgeDetector(res, str(image['edgeAlgorithm'])) # detect edges
    saveFile(imagename + '_edge.png', edge)
    print('edge')
    inv = inverter(edge) # invert result
    saveFile(imagename + '_inv.png', inv) # save file
    print('inv')
    result = imageAsArray(imagename + '_inv.png', image['treshold']) # store as array
    saveFile(imagename + '_result.png', result)
    print('result')
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' + imagename + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' + imagename + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' + imagename + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' + imagename + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' + imagename + '_result.png']))

tester()
