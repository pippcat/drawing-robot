#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import serial
import time
import struct
from vpython import *
import numpy as np
 
#Start the serial port to communicate with arduino
#data = serial.Serial('com3',9600, timeout=1)

innerArmLength = 10
outerArmLength = 15
innerPos = vector(0,-10,0) # origin of inner arm
innerLength = vector(0,innerArmLength,0) # length of inner arm
outerPos = innerPos + innerLength # origin of outer arm
outerLength = vector(0,outerArmLength,0) # length of outer arm

def draw_line(axis,position):
    if axis == "y":
        return box(pos=position, length=40, height=0.02, width=0.02)   
    if axis == "x":
        return box(pos=position, length=0.02, height=20, width=0.02)   

def setup_scenery():
    scene = canvas(title='Drawing robot simulation', width=1600, height=900) 
    
    #Create virtual environment:
    #first we create the arrows which represent the arms:
    innerArm = arrow(pos=(innerPos), axis=(innerLength), shaftwidth=0.4, headwidth=0.6, color=color.blue)
    outerArm = arrow(pos=(outerPos), axis=(outerLength), shaftwidth=0.4, headwidth=0.6, color=color.red)
    #and the now the labels
    angleLabel = label (text = 'Servo angle is: 90', pos=(vector(0,5,0)), height=15, box=False)
    angle0 = label (text = '0', pos=(vector(-10,-10,0)), height=15, box=False)
    angle45 = label (text = '45', pos=(vector(-7.5,-2.5,0)), height=15, box=False)
    angle90 = label (text = '90', pos=(vector(0,1,0)), height=15, box=False)
    angle135 = label (text = '135', pos=(vector(7.5,-2.5,0)), height=15, box=False)
    angle180 = label (text = '180', pos=(vector(10,-10,0)), height=15, box=False)
    box(pos=vector(0,0,-1), length=40, height=20, width=0.02)
    for i in range(-20,21,1): # drawing area, pixelated
        draw_line('y',vector(0,i/2,0))
    for i in range(-40,41,1): # drawing area, pixelated
        draw_line('x',vector(i/2,0,0))
    return {'angleLabel':angleLabel, 'innerArm':innerArm, 'outerArm':outerArm, 'innerLength':innerLength, 'outerLength':outerLength}
# this stores a image as an array of 0s and 1s:
    #filename = 'out.png'
    #image = np.asarray(os.getcwd() + '/images/' + filename)

def dummy(angleLabel,innerArm,outerArm,innerLength,outerLength):# dummy function
    while (1==1):
        rate(20) #refresh rate required for VPython
        posx = int(input('x coordinate? '))
        posy = int(input('y coordinate? '))
        cosb = (innerArmLength*innerArmLength+outerArmLength*outerArmLength - posx * posx - posy*posy)/(innerArmLength*innerArmLength + outerArmLength * outerArmLength)
        b = np.cos(cosb)
        a = innerArmLength * np.tan(posx/posy) + b/2
        print('alpha = ' + str(a))
        print('beta = ' + str(b))
        innerArm.axis=(vector(-innerArmLength*np.cos(float(a)*0.01745),innerArmLength*np.sin(float(a)*0.01745),0)) #calculate the new axis of the indicator
        outerArm.pos=(innerPos + innerArm.axis)
       # for pos in range(0,180,10):
       #     time.sleep(0.2)
       #     myLabel = 'Servo angle is: '+str(pos) #update the text of the label for the virtual environment
            #data.write(struct.pack('>B',pos)) #code and send the angle to the Arduino through serial port
       #     angleLabel.text = myLabel #refresh label on virtual environment
       #     innerArm.axis=(vector(-10*np.cos(float(pos)*0.01745),10*np.sin(float(pos)*0.01745),0)) #calculate the new axis of the indicator
       #     outerArm.pos=(vector(-10*np.cos(float(pos)*0.01745),10*np.sin(float(pos)*0.01745),0)-innerLength) #calculate the new axis of the indicator
       #     for posout in range(0,180,10):
       #         time.sleep(0.2)
       #         outerArm.axis=(vector(-10*np.cos(float(posout)*0.01745),10*np.sin(float(posout)*0.01745),0)) #calculate the new axis of the indicator
