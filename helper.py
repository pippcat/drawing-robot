#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# shared helper functions for simulator and robots

### calculate the angles of the two servos:
def getAngles(x, y):
    try:
        r_2 = x**2 + y**2
        l_sq = l1**2 + l2**2
        term2 = (r_2 - l_sq)/(2*l1*l2)
        term1 = ((1 - term2**2)**0.5)*-1
        # calculate outer angle
        outerAngle = math.atan2(term1, term2)
        k1 = l1 + l2*math.cos(th2)
        k2 = l2*math.sin(th2)
        r  = (k1**2 + k2**2)**0.5
        gamma = math.atan2(k2,k1)
        # calculate inner angle
        innerAngle = math.atan2(y,x) - gamma
        # return angles:
        return innerAngle, outerAngle
    except:
        print("not possible, will return (0,0)")
        return 0,0

### finds the first pixel of the next line:
def findPixel(image):
    for ix in range(image.shape[0]):
        for iy in range(image.shape[1]):
            #print("ix: " + str(ix) + ", iy: " + str(iy) + ", image[ix,iy]: " + str(image[ix,iy]))
            if image[ix,iy] < 0.5:
                image[ix,iy] = 1
                return ix,iy
    return False,False

### finds the next pixel in a line:
def findAdjacentPixel(image,ix,iy):
    ax=ix
    for ay in range(iy+1,iy-1,-1):
        if image[ax,ay] < 0.5:
            image[ax,ay] = 1
            return ax,ay
        for ax in range(ix+1,ix-1,-1):
            #print("fap: ix: "+str(ix)+", iy: "+str(iy)+", ax: "+str(ax)+", ay: "+str(ay)+", image: "+str(image[ax,ay]))
            if image[ax,ay] < 0.5:
                image[ax,ay] = 1
                return ax,ay
    return False,False
