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
    if direction == "up":
        print("pen up!")
        arms['penMotor'].angle = arms['penUpAngle']
    time.sleep(raspi['waitTimePen']) # check how small it could be!

def calibrate(arms, raspi, motor, angle, direction=False):
    print('Calibrating', motor, 'moving to', angle, 'degrees.')
    if motor == "innerArm":
        arms['innerArm'].angle = angle
    elif motor == "outerArm":
        arms['outerArm'].angle = angle
    elif motor == "pen":
        if direction == "down":
            movePen(arms, raspi, "down")
        if direction == "up":
            movePen(arms, raspi, "up")
    time.sleep(1)
