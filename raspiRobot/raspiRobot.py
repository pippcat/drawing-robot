#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# the drawing robot, implemented for a RaspberryPi

import time
import logging
import board
import busio
import adafruit_pca9685
import adafruit_motor.servo

def set_up_raspi(arms, raspi):
    '''
    Initializes the drawing robot.

    :param arms: arms dictionary
    :param raspi: raspi dictionary
    '''

    logging.info('Initializing drawing robot.')
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

def set_angle(arms, raspi, distance):
    '''
    Moves the robot arms to the right position to draw the current pixel.

    :param arms: arms dictionary
    :param raspi: raspi dictionary
    '''
    arms['innerArm'].angle = 180 - arms['innerArmAngleDeg']
    arms['outerArm'].angle = arms['outerArmAngleDeg']
    if distance == "far":
        time.sleep(raspi['waitTimeFar']) # check how small it could be!
    # we dont have to wait long for new angles found by findAdjacentPixel(), because changes are always very small:
    if distance == "near":
        time.sleep(raspi['waitTimeNear']) # check how small it could be!

def move_pen(arms, raspi, direction):
    '''
    Moves the pen up and down.

    :param arms: arms dictionary
    :param raspi: raspi dictionary
    :param direction: either "up" or "down"
    '''

    if direction == "down":
        logging.info("pen down!")
        arms['penMotor'].angle = arms['penDownAngle']
    if direction == "up":
        logging.info("pen up!")
        arms['penMotor'].angle = arms['penUpAngle']
    time.sleep(raspi['waitTimePen']) # check how small it could be!

def move_then_down(arms, raspi):
    '''
    Moves the arm and then lowers pen.

    :param arms: arms dictionary
    :param raspi: raspi dictionary
    '''

    set_angle(arms, raspi, 'far')
    move_pen(arms, raspi, 'down')

def calibrate(arms, raspi, motor, angle, direction=False):
    '''
    Can be used to check the calibration of the robot arms.

    :param arms: arms dictionary
    :param raspi: raspi dictionary
    :param motor: either "innerArm", "outerArm" oder "pen"
    :param angle: angle to move the selected motor to
    :param direction: either "up" or "down", defaults to False
    '''

    logging.info('Calibrating ' + motor + ' moving to ' + angle + ' degrees.')
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
