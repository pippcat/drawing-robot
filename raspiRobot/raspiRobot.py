#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# the drawing robot, implemented for a RaspberryPi

from __future__ import division
import time
import board
import busio
import adafruit_pca9685
import adafruit_motor.servo
import traceback
import helper
import math

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

innerArmChannel = pca.channels[arms['innerArmChannel']]
outerArmChannel = pca.channels[arms['outerArmChannel']]
penMotorChannel = pca.channels[arms['penMotorChannel']]
pca.frequency = arms['frequency']

innerArm = adafruit_motor.servo.Servo(innerArmChannel, actuation_range=arms['innerArmActuationRange'],
        min_pulse=arms['innerArmMinPulse'], max_pulse=arms['innerArmMaxPulse'])
outerArm = adafruit_motor.servo.Servo(outerArmChannel, actuation_range=arms['iouterArmActuationRange'],
        min_pulse=arms['innerArmMinPulse'], max_pulse=arms['innerArmMaxPulse'])
penMotor = adafruit_motor.servo.Servo(penMotorChannel)


### function to set an arm to an angle:
def setAngle(arms, image):
    innerArm.angle = 180 - arms['innerArmAngleDeg']
    outerArm.angle = arms['outerArmAngleDeg']
    if image['distance'] == "far":
        time.sleep(raspi['waitTimeFar']) # check how small it could be!
    # we dont have to wait long for new angles found by findAdjacentPixel(), because changes are always very small:
    if image['distance'] == "near":
        time.sleep(raspi['waitTimeNear']) # check how small it could be!

### function to move penMotor up and down:
def movePen(direction, waitTime):
    upAngle = 80 # check values!
    downAngle = 110
    if direction == "down":
        print("pen down!")
        penMotor.angle = downAngle
    if direction == "up":
        print("pen up!")
        penMotor.angle = upAngle
    time.sleep(waitTime) # check how small it could be!

def calibrate(motor):
    if motor == "innerArm":
        print("Calibrating innerArm")
        for i in range(0,181,45):
            print("moving to " + str(i) + " degrees")
            innerArm.angle = i
            input("press button to continue!")
        print("finished, moving to 90 degrees")
        innerArm.angle = 90
        time.sleep(1)
    elif motor == "outerArm":
        print("Calibrating outerArm")
        for i in range(0,180,45):
            print("moving to " + str(i) + " degrees")
            outerArm.angle = i
            input("press button to continue!")
        print("finished, moving to 90 degrees")
        outerArm.angle = 90
        time.sleep(1)
    elif motor == "pen":
        print("Calibrating penMotor")
        print("moving pen down")
        movePen("down")
        input("press button to continue!")
        print("moving pen up")
        movePen("up")
        input("press button to continue!")
