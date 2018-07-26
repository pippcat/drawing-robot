#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import serial
import time
import struct
from vpython import *
import numpy as np
import math
from skimage.io import imread 
#Start the serial port to communicate with arduino
#data = serial.Serial('com3',9600, timeout=1)

innerArmLength = 100
outerArmLength = 80
innerPos = vector(0,0,0) # origin of inner arm
innerLength = vector(innerArmLength,0,0) # length of inner arm
outerPos = innerPos + innerLength # origin of outer arm
outerLength = vector(outerArmLength,0,0) # length of outer arm

def draw_line(axis,position,linecolor):
    if axis == "y":
        #return box(pos=position, length=400, height=0.2, width=0.2)   
        return curve(vector(position)-vector(200,0,0), vector(position)+vector(200,0,0), radius=0.5, color=linecolor)
    if axis == "x":
        return curve(vector(position)-vector(0,100,0), vector(position)+vector(0,100,0), radius=0.5, color=linecolor)

def setup_scenery(image):
    scene = canvas(title='Drawing robot simulation', width=1600, height=900) 
    
    #Create virtual environment:
    #first we create the arrows which represent the arms:
    innerArm = arrow(pos=(innerPos), axis=(innerLength), shaftwidth=4, headwidth=6, color=color.blue)
    outerArm = arrow(pos=(outerPos), axis=(outerLength), shaftwidth=4, headwidth=6, color=color.red)
    #and the now the labels
    alphaLabel = label (text = 'First servo angle is: 0', pos=(vector(0,-20,0)), height=15, box=False)
    betaLabel = label (text = 'Second servo angle is: 0', pos=(vector(0,-40,0)), height=15, box=False)
    maxRange = ring(pos=vector(0,0,0), axis=vector(0,0,1), radius=innerArmLength+outerArmLength, thickness=1, color=color.cyan)
    for i in range(0,205,5): # drawing area, pixelated
        if i%50 == 0:
            draw_line('y',vector(0,i,0),color.white)
        else:
            draw_line('y',vector(0,i,0),color.gray(0.2))
    for i in range(-200,205,5): # drawing area, pixelated
        if i%50 == 0:
            draw_line('x',vector(i,100,0),color.white)
        else:
            draw_line('x',vector(i,100,0),color.gray(0.2))
    image_scale = image.shape[0]/(innerArmLength+outerArmLength)
    image_shift_x = (image.shape[0]/image_scale)/2
    for ix in range(image.shape[0]):
        for iy in range(image.shape[1]):
            if image[ix,iy] < 0.5:
                box(pos=vector((ix/image_scale-image_shift_x),iy/image_scale,0.1), length=1, height=1, width=1, color=color.green)
    return {'alphaLabel':alphaLabel, 'betaLabel':betaLabel, 'innerArm':innerArm, 'outerArm':outerArm, 'innerLength':innerLength, 'outerLength':outerLength, 'image':image, 'image_scale':image_scale, 'image_shift_x':image_shift_x}

l1 = innerArmLength #Length of link 1
l2 = outerArmLength #length of link 2

#IK for just the 2 links
def getangles(x, y):
    """Returns the angles of the first two links
       in the robotic arm as a list.
       returns -> (th1, th2)"""
    try:    #stuff for calculating th2
        r_2 = x**2 + y**2
        l_sq = l1**2 + l2**2
        term2 = (r_2 - l_sq)/(2*l1*l2)
        term1 = ((1 - term2**2)**0.5)*-1
        #calculate th2
        th2 = math.atan2(term1, term2)
        k1 = l1 + l2*math.cos(th2)
        k2 = l2*math.sin(th2)
        r  = (k1**2 + k2**2)**0.5
        gamma = math.atan2(k2,k1)
        #calculate th1
        th1 = math.atan2(y,x) - gamma
        return th1, th2
    except:
        print("not possible, will return (0,0)")
        return 0,0

def find_pixel(image):
    for ix in range(image.shape[0]):
        for iy in range(image.shape[1]):
            #print("ix: " + str(ix) + ", iy: " + str(iy) + ", image[ix,iy]: " + str(image[ix,iy]))           
            if image[ix,iy] < 0.5:
                image[ix,iy] = 1
                return ix,iy
    return False,False

def find_adjacent_pixel(image,ix,iy):
    for ay in range(iy-1,ix+1,1):
        for ax in range(ix-1,ix+1,1):
            print("ix: "+str(ix)+", iy: "+str(iy)+", ax: "+str(ax)+", ay: "+str(ay)+", image: "+str(image[ax,ay]))
            if image[ax,ay] < 0.5:
                image[ax,ay] = 1
                return ax,ay
    return False,False

def draw_image(alphaLabel,betaLabel,innerArm,outerArm,innerLength,outerLength,image,image_scale,image_shift_x):# dummy function
    ax=ix=ay=ix=False
    alpha=beta=0
    while (1==1):
        rate(20) #refresh rate required for VPython
        ix,iy = find_pixel(image)
        if ix and iy:
                alpha, beta = getangles(ix/image_scale-image_shift_x,iy/image_scale)
                if alpha != 0 and beta != 0:
                    drive_arms(alpha,beta,ix,iy,innerArm,outerArm,innerLength,outerLength,alphaLabel,betaLabel,image_scale,image_shift_x)
                    c = curve(vector(ix/image_scale - image_shift_x,iy/image_scale,1))
                    ax,ay = find_adjacent_pixel(image,ix,iy)
                    print('ax: ' + str(ax)+ '; ay: ' + str(ay))
                    while (ax and ay):
                        c.append(vector(ax/image_scale - image_shift_x,ay/image_scale,1))
                        alpha, beta = getangles(ax/image_scale-image_shift_x,ay/image_scale)
                        if alpha != 0 and beta != 0:
                            drive_arms(alpha,beta,ax,ay,innerArm,outerArm,innerLength,outerLength,alphaLabel,betaLabel,image_scale,image_shift_x)
                        ax,ay = find_adjacent_pixel(image,ax,ay)
        else:
            print("Nothing left to draw!")
            return
        print("ix: " + str(ix) + ", iy: " + str(iy) + ", ax: " + str(ax) + ", ay: " + str(ay) + ", alpha: " + str(alpha) + ", beta: " + str(beta))
        time.sleep(0.3)
    
def drive_arms(alpha, beta,x,y,innerArm,outerArm,innerLength,outerLength,alphaLabel,betaLabel,image_scale,image_shift_x):
    #box(pos=vector(x/image_scale-image_shift_x,y/image_scale,1), length=1, height=1, width=1, color=color.cyan)
    innerArm.axis = innerLength # reset arm to 0 deg
    innerArm.axis = rotate(innerArm.axis, angle=alpha, axis=(vector(0,0,1))) # rotate it using alpha
    outerArm.pos=(innerPos + innerArm.axis) # calculate starting point of second arm
    outerArm.axis = innerArm.axis # set orientation equal to first arm
    outerArm.length = outerArmLength # reset length of arm
    outerArm.axis = rotate(outerArm.axis, angle=beta, axis=(vector(0,0,1))) # rotate it
    alphaLabel.text = "First servo angle is: " + str(np.rad2deg(alpha))
    betaLabel.text = "Second servo angle is: " + str(np.rad2deg(beta))
