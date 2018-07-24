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

innerpos = vector(0,-10,0)
innerlength = vector(0,10,0)
outerpos = innerpos + innerlength
outerlength = vector(0,10,0)
#Create virtual environment:
#first we create the arrow to show current position of the servo
innerArm = arrow(pos=(innerpos), axis=(innerlength), shaftwidth=0.4, headwidth=0.6)
outerArm = arrow(pos=(outerpos), axis=(outerlength), shaftwidth=0.4, headwidth=0.6)
#and the now the labels
angleLabel = label (text = 'Servo angle is: 90', pos=(vector(0,5,0)), height=15, box=False)
angle0 = label (text = '0', pos=(vector(-10,-10,0)), height=15, box=False)
angle45 = label (text = '45', pos=(vector(-7.5,-2.5,0)), height=15, box=False)
angle90 = label (text = '90', pos=(vector(0,1,0)), height=15, box=False)
angle135 = label (text = '135', pos=(vector(7.5,-2.5,0)), height=15, box=False)
angle180 = label (text = '180', pos=(vector(10,-10,0)), height=15, box=False)

for i in range(-5,6,1):
    draw_line('x',vector(0,i,0))
    draw_line('y',vector(i,0,0))

#now we made an infinite while loop to keep the program running
#filename = 'out.png'
#image = np.asarray(os.getcwd() + '/images/' + filename)
#tex = materials.texture(data=image, mapping="rectangular", interpolate=False)
#box( color=color.black, texture='/images/out.png')
while (1==1):
    rate(20) #refresh rate required for VPython
#    pos = input("Enter a number: ") #Prompt the user for the angle
    for pos in range(0,180,1):
        time.sleep(0.2)
        myLabel = 'Servo angle is: '+str(pos) #update the text of the label for the virtual environment
        #data.write(struct.pack('>B',pos)) #code and send the angle to the Arduino through serial port
        angleLabel.text = myLabel #refresh label on virtual environment
        innerArm.axis=(vector(-10*np.cos(float(pos)*0.01745),10*np.sin(float(pos)*0.01745),0)) #calculate the new axis of the indicator
        outerArm.pos=(vector(-10*np.cos(float(pos)*0.01745),10*np.sin(float(pos)*0.01745),0)-innerlength) #calculate the new axis of the indicator

