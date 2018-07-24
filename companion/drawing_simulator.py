#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import serial
import time
import struct
from vpython import *
import numpy as np
 
#Start the serial port to communicate with arduino
#data = serial.Serial('com3',9600, timeout=1)

def draw_line(axis,position):
    if axis == "x":
        return box(pos=position, length=10, height=0.1, width=0.1)   
    if axis == "y":
        return box(pos=position, length=0.1, height=10, width=0.1)   

def setup_scenery():
    innerPos = vector(0,-10,0) # origin of inner arm
    innerLength = vector(0,10,0) # length of inner arm
    outerPos = innerPos + innerLength # origin of outer arm
    outerLength = vector(0,10,0) # length of outer arm
    
    #Create virtual environment:
    #first we create the arrows which represent the arms:
    innerArm = arrow(pos=(innerPos), axis=(innerLength), shaftwidth=0.4, headwidth=0.6)
    outerArm = arrow(pos=(outerPos), axis=(outerLength), shaftwidth=0.4, headwidth=0.6)
    #and the now the labels
    angleLabel = label (text = 'Servo angle is: 90', pos=(vector(0,5,0)), height=15, box=False)
    angle0 = label (text = '0', pos=(vector(-10,-10,0)), height=15, box=False)
    angle45 = label (text = '45', pos=(vector(-7.5,-2.5,0)), height=15, box=False)
    angle90 = label (text = '90', pos=(vector(0,1,0)), height=15, box=False)
    angle135 = label (text = '135', pos=(vector(7.5,-2.5,0)), height=15, box=False)
    angle180 = label (text = '180', pos=(vector(10,-10,0)), height=15, box=False)

    for i in range(-5,6,1): # drawing area, pixelated
        draw_line('x',vector(0,i,0))
        draw_line('y',vector(i,0,0))
    return {'angleLabel':angleLabel, 'innerArm':innerArm, 'outerArm':outerArm, 'innerLength':innerLength, 'outerLength':outerLength}
# this stores a image as an array of 0s and 1s:
#filename = 'out.png'
#image = np.asarray(os.getcwd() + '/images/' + filename)

def dummy(angleLabel,innerArm,outerArm,innerLength,outerLength):# dummy function
    while (1==1):
        rate(20) #refresh rate required for VPython
        for pos in range(0,180,1):
            time.sleep(0.2)
            myLabel = 'Servo angle is: '+str(pos) #update the text of the label for the virtual environment
            #data.write(struct.pack('>B',pos)) #code and send the angle to the Arduino through serial port
            angleLabel.text = myLabel #refresh label on virtual environment
            innerArm.axis=(vector(-10*np.cos(float(pos)*0.01745),10*np.sin(float(pos)*0.01745),0)) #calculate the new axis of the indicator
            outerArm.pos=(vector(-10*np.cos(float(pos)*0.01745),10*np.sin(float(pos)*0.01745),0)-innerLength) #calculate the new axis of the indicator

