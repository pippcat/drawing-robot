#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# the drawing robot, implemented for a RaspberryPi

import RPi.GPIO as GPIO
import traceback
import helper
import math
from time import sleep

### set up hardware
innerArmPin = 17
outerArmPin = 27
penMotorPin = 22

GPIO.setmode(GPIO.BCM)
# inner arm
GPIO.setup(innerArmPin, GPIO.OUT) # we want it as output
innerArm = GPIO.PWM(innerArmPin, 50) # GPIO 17 as PWM with 50Hz
innerArm.start(0) # do nothing
# outer arm
GPIO.setup(outerArmPin, GPIO.OUT) # we want it as output
outerArm = GPIO.PWM(outerArmPin, 50) # GPIO 17 as PWM with 50Hz
outerArm.start(0) # do nothing
# penMotor
GPIO.setup(penMotorPin, GPIO.OUT) # we want it as output
penMotor = GPIO.PWM(penMotorPin, 50) # GPIO 17 as PWM with 50Hz
penMotor.start(0) # do nothing

### function to set an arm to an angle:
def setAngle(innerAngle, outerAngle, pixel):
    innerDuty = innerAngle / 36 + 5 # some calculation depending on your servo, see https://www.instructables.com/id/Servo-Motor-Control-With-Raspberry-Pi/
    outerDuty = outerAngle / 36 + 5 # some calculation depending on your servo, see https://www.instructables.com/id/Servo-Motor-Control-With-Raspberry-Pi/
    GPIO.output(innerArmPin, True)
    GPIO.output(outerArmPin, True)
    innerArm.ChangeDutyCycle(innerDuty)
    outerArm.ChangeDutyCycle(outerDuty)
    if pixel == "new":
        sleep(1) # check how small it could be!
    # we dont have to wait long for new angles found by findAdjacentPixel(), because changes are always very small:
    if pixel == "near":
        sleep(0.5) # check how small it could be!
    GPIO.output(innerArmPin, False)
    GPIO.output(outerArmPin, False)
    innerArm.ChangeDutyCycle(0)
    outerArm.ChangeDutyCycle(0)

### function to move penMotor up and down:
def movePen(direction):
    GPIO.output(penMotorPin, True)
    upAngle = 50 # check values!
    downAngle = 100
    if direction == "down":
        print("pen down!")
        duty = downAngle / 18 + 2
        penMotor.ChangeDutyCycle(duty)
    if direction == "up":
        print("pen up!")
        duty = upAngle / 18 + 2
        penMotor.ChangeDutyCycle(duty)
    sleep(1) # check how small it could be!
    GPIO.output(penMotorPin, False)
    penMotor.ChangeDutyCycle(0)

def drawImage(innerLength,outerLength,origin,image,image_scale):
    ax=ix=ay=ix=False
    alpha=beta=0
    movePen("up")
    try:
        print("drawImage initialisation. innerLength = " + str(innerLength) + ", outerLength = " + str(outerLength) + ", origin = " + str(origin) + ", image_scale = " + str(image_scale))
        while True:
            ix,iy = helper.findPixel(image)
            if (ix and iy):
                alpha, beta = helper.getAngles((ix/image_scale+origin['x']),iy/image_scale+origin['y'],innerLength,outerLength)
                print("### ix: " + str(ix) + ", iy: " + str(iy) + ", innerAngle: "+str(int(math.degrees(alpha)))+"; outerAngle: "+str(int(math.degrees(beta))))
                if alpha != 0 and beta != 0:
                    movePen("down")
                    setAngle(alpha,beta,'new')
                    ax,ay = helper.findAdjacentPixel(image,ix,iy)
                    print("### ax: " + str(ax) + ", ay: " + str(ay) + ", innerAngle: "+str(int(math.degrees(alpha)))+"; outerAngle: "+str(int(math.degrees(beta))))
                    while (ax and ay):
                        alpha, beta = helper.getAngles(ax/image_scale+origin['x'],ay/image_scale+origin['y'],innerLength,outerLength)
                        if alpha != 0 and beta != 0:
                            setAngle(alpha,beta,'near')
                        ax,ay = helper.findAdjacentPixel(image,ax,ay)
                        print("### ax: " + str(ax) + ", ay: " + str(ay) + ", innerAngle: "+str(int(math.degrees(alpha)))+"; outerAngle: "+str(int(math.degrees(beta))))
                movePen("up")
            else:
                print("Nothing left to draw!")
                innerArm.stop()
                outerArm.stop()
                penMotor.stop()
                GPIO.cleanup()
                print("Finished GPIO cleanup")
                return
            #print("ix: " + str(ix) + ", iy: " + str(iy) + ", ax: " + str(ax) + ", ay: " + str(ay) + ", alpha: " + str(alpha) + ", beta: " + str(beta))
    except:
        print("Drawing was interrupted!")
        traceback.print_exc()
        innerArm.stop()
        outerArm.stop()
        penMotor.stop()
        GPIO.cleanup()
        print("Finished GPIO cleanup")
