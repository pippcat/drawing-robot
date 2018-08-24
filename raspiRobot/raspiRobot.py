#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# the drawing robot, implemented for a RaspberryPi

import RPi.GPIO as GPIO
from time import sleep

### set up hardware
innerArmPin = 17
outerArmPin = 27
penPin = 22
GPIO.setmode(GPIO.BCM)
# inner arm
GPIO.setup(innerArmPin, GPIO.OUT) # we want it as output
innerArm = GPIO.PWM(innerArmPin, 50) # GPIO 17 as PWM with 50Hz
innerArm.start(0) # do nothing
# outer arm
GPIO.setup(outerArmPin, GPIO.OUT) # we want it as output
outerArm = GPIO.PWM(outerArmPin, 50) # GPIO 17 as PWM with 50Hz
outerArm.start(0) # do nothing
# pen
GPIO.setup(penPin, GPIO.OUT) # we want it as output
pen = GPIO.PWM(penPin, 50) # GPIO 17 as PWM with 50Hz
pen.start(0) # do nothing

### function to set an arm to an angle:
def setAngle(angle, arm):
    duty = angle / 18 + 2 # some calculation depending on your servo, see https://www.instructables.com/id/Servo-Motor-Control-With-Raspberry-Pi/
    if arm == "innerArm":
        moveArm = innerArm
        moveArmPin = innerArmPin
    if arm == "outerArm":
        moveArm = outerArm
        moveArmPin = outerArmPin
    GPIO.output(moveArmPin, True)
    moveArm.ChangeDutyCycle(duty)
    sleep(1) # check how small it could be!
    GPIO.output(moveArmPin, False)
    moveArm.ChangeDutyCycle(0)

### function to move pen up and down:
def movePen(direction):
    GPIO.output(penPin, True)
    duty = 50 # check values!
    if direction == "down":
        pen.ChangeDutyCycle(-duty)
    if direction == "up":
        pen.ChangeDutyCycle(duty)
    sleep(1) # check how small it could be!

def drawImage(innerLength,outerLength,origin,image,image_scale):
    ax=ix=ay=ix=False
    alpha=beta=0
    movePen("up")
    try:
        while True:
            ix,iy = helper.find_pixel(image)
            if (ix and iy):
                alpha, beta = helper.getAngles((ix/image_scale+origin['x']),iy/image_scale+origin['x'])
                #print("### alpha: "+str(alpha)+"; beta: "+str(beta))
                if alpha != 0 and beta != 0:
                    movePen("down")
                    setAngle(alpha,'innerArm')
                    setAngle(beta,'outerArm')
                    ax,ay = helper.findAdjacentPixel(image,ix,iy)
                    #print('### ax: ' + str(ax)+ '; ay: ' + str(ay))
                    while (ax and ay):
                        alpha, beta = getAngles(ax/image_scale+origin['x'],ay/image_scale+origin['y'])
                        if alpha != 0 and beta != 0:
                            setAngle(alpha,'innerArm')
                            setAngle(beta,'outerArm')
                        ax,ay = find_adjacent_pixel(image,ax,ay)
                        #print('###### ax: ' + str(ax)+ '; ay: ' + str(ay))
                movePen("up")
            else:
                print("Nothing left to draw!")
                innerArm.stop()
                outerArm.stop()
                pen.stop()
                GPIO.cleanup()
                print("Finished GPIO cleanup")
                return
            #print("ix: " + str(ix) + ", iy: " + str(iy) + ", ax: " + str(ax) + ", ay: " + str(ay) + ", alpha: " + str(alpha) + ", beta: " + str(beta))
    except:
        print("Drawing was interrupted!")
        innerArm.stop()
        outerArm.stop()
        pen.stop()
        GPIO.cleanup()
        print("Finished GPIO cleanup")
