#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# the drawing robot, implemented for a RaspberryPi

import time
import board
import busio
import adafruit_pca9685
import adafruit_motor.servo

def setupRaspi(arms, raspi):
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = adafruit_pca9685.PCA9685(i2c)
    pca.frequency = raspi['frequency']
    innerArm = adafruit_motor.servo.Servo(pca.channels[arms['innerArmChannel']], actuation_range=arms['innerArmActuationRange'],
            min_pulse=arms['innerArmMinPulse'], max_pulse=arms['innerArmMaxPulse'])
    outerArm = adafruit_motor.servo.Servo(pca.channels[arms['outerArmChannel']], actuation_range=arms['outerArmActuationRange'],
             min_pulse=arms['innerArmMinPulse'], max_pulse=arms['innerArmMaxPulse'])
    penMotor = adafruit_motor.servo.Servo(pca.channels[arms['penChannel']])
    arms['innerArm'] = innerArm
    arms['outerArm'] = outerArm
    arms['penMotor'] = penMotor

### function to set an arm to an angle:
def setAngle(arms, raspi, distance):
    arms['innerArm'].angle = 180 - arms['innerArmAngleDeg']
    arms['outerArm'].angle = arms['outerArmAngleDeg']
    if distance == "far":
        time.sleep(raspi['waitTimeFar']) # check how small it could be!
    # we dont have to wait long for new angles found by findAdjacentPixel(), because changes are always very small:
    if distance == "near":
        time.sleep(raspi['waitTimeNear']) # check how small it could be!

### function to move penMotor up and down:
def movePen(arms, raspi, direction):
    if direction == "down":
        print("pen down!")
        arms['penMotor'].angle = arms['penDownAngle']
        print(arms['penMotor'], arms['penDownAngle'],raspi['waitTimePen'])
    if direction == "up":
        print("pen up!")
        arms['penMotor'].angle = arms['penUpAngle']
    time.sleep(raspi['waitTimePen']) # check how small it could be!

def calibrate(arms, raspi, motor):
    if motor == "innerArm":
        print("Calibrating innerArm")
        for i in range(0,180,45):
            print("moving to " + str(i) + " degrees")
            arms['innerArm'].angle = i
            input("press button to continue!")
        print("finished, moving to 90 degrees")
        arms['innerArm'].angle = 90
        time.sleep(1)
    elif motor == "outerArm":
        print("Calibrating outerArm")
        for i in range(0,180,45):
            print("moving to " + str(i) + " degrees")
            arms['outerArm'].angle = i
            input("press button to continue!")
        print("finished, moving to 90 degrees")
        arms['outerArm'].angle = 90
        time.sleep(1)
    elif motor == "pen":
        print("Calibrating penMotor")
        print("moving pen down")
        movePen(arms, raspi, "down")
        input("press button to continue!")
        print("moving pen up")
        movePen(arms, raspi, "up")
        input("press button to continue!")
