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
import raspiRobot.raspiRobot

# variables:
innerArmLength = 136
outerArmLength = 75
ArmLength = innerArmLength + outerArmLength
origin = {'x':ArmLength/8,'y':ArmLength/6} # origin of robot with respect to (0/0)
image = image_manipulator.image_as_array('out.png', 0.9)
image_scale = 1.6*image.shape[0]/(ArmLength)

def drawImage(image):
    print("drawing image")
    raspiRobot.raspiRobot.drawImage(innerArmLength,outerArmLength,origin,image,image_scale)

draw_simulation(image)
