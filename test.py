#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# external libraries:
from dialog import Dialog
from datetime import datetime
from subprocess import call
import os
import sys
import math

# own stuff:
import helper
import raspiRobot.raspiRobot_PCA9685
import imageProcessor.imageProcessor

# variables:
treshold = 0.73 # treshold for grayscale to binary conversion
innerArmLength = 200
outerArmLength = 122
ArmLength = innerArmLength + outerArmLength
origin = {'x':ArmLength/2,'y':ArmLength/8} # origin of robot with respect to (0/0)
image = imageProcessor.imageProcessor.imageAsArray('out.png', 0.7)
image_scale = 3*image.shape[0]/(ArmLength)

def drawImage(image):
    print("drawing image")
    raspiRobot.raspiRobot_PCA9685.drawImage(innerArmLength,outerArmLength,origin,image,image_scale)

try:
    # while True:
    #     angle = input("Angle?: ")
    #     raspiRobot.raspiRobot.setAngle(int(angle),int(angle),'near')
    drawImage(image)
    #raspiRobot.raspiRobot_PCA9685.calibrate("pen")

except KeyboardInterrupt:
    raspiRobot.raspiRobot_PCA9685.movePen("up")
    raspiRobot.raspiRobot_PCA9685.setAngle(90,90,"new")
    raspiRobot.raspiRobot_PCA9685.release()
