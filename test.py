#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from imageProcessor.imageProcessor import *
import string
from random import choice
import os
from bokeh.models import ColumnDataSource
from raspiRobot.raspiRobot import *


# i2c = busio.I2C(board.SCL, board.SDA)
# pca = adafruit_pca9685.PCA9685(i2c)

arms = {'innerArmLength':136, 'innerArmAngleRad':0, 'innerArmAngleDeg':0, 'innerArmChannel':0,
            'innerArmActuationRange':180, 'innerArmMinPulse':700, 'innerArmMaxPulse':2450,
       'outerArmLength':115, 'outerArmAngleRad':0, 'innerArmAngleDeg':0, 'outerArmChannel':1,
            'outerArmActuationRange':180, 'outerArmMinPulse':850, 'outerArmMaxPulse':2750,
       'penUpAngle':80, 'penDownAngle':110,'penChannel':2,
       'armLength': 136 + 115, 'frequency' : 50}

raspi = {'switchedOn':True, 'frequency':50, 'waitTimeNear':0.05, 'waitTimeFar':0.3, 'waitTimePen':1}

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

try:
    setupRaspi(arms, raspi)
     #while True:
    #     angle = input("Angle?: ")
    #     raspiRobot.raspiRobot_PCA9685.setAngle(float(angle),float(angle),'new')
#    drawImage(image)
    #calibrate(arms, raspi, "pen")
    #calibrate(arms, raspi, "innerArm")
    #calibrate(arms, raspi, "outerArm")

except KeyboardInterrupt:
    movePen("up")
    setAngle(90,90,"new")
    release()

#tester()
