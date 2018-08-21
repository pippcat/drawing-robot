#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# the drawing robot, implemented for a RaspberryPi

import RPi.GPIO as GPIO
from time import sleep

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 als PWM mit 50Hz
p.start(0) # do nothing

def setAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(servoPIN, True)
    p.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(servoPIN, False)
    p.ChangeDutyCycle(0)

try:
    while True:
        angle = input("Angle?: ")
        setAngle(int(angle))

except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()
