#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# shared helper functions for simulator and robots

import traceback
import math
### calculate the angles of the two servos:
def getAngles(x, y, innerArmLength, outerArmLength):
    try:
        r_2 = x**2 + y**2
        l_sq = innerArmLength**2 + outerArmLength**2
        term2 = (r_2 - l_sq)/(2*innerArmLength*outerArmLength)
        term1 = ((1 - term2**2)**0.5)*-1
        # calculate outer angle
        outerAngle = math.atan2(term1, term2)
        k1 = innerArmLength + outerArmLength*math.cos(outerAngle)
        k2 = outerArmLength*math.sin(outerAngle)
        r  = (k1**2 + k2**2)**0.5
        gamma = math.atan2(k2,k1)
        # calculate inner angle
        innerAngle = math.atan2(y,x) - gamma
        # outer angle seems to be always negative, therefore add 180°:
        outerAngle += math.pi
        innerAngleDeg = math.degrees(innerAngle)
        outerAngleDeg = math.degrees(outerAngle)
        # return angles, since outer angle is always negative, shift it by 180°
        return innerAngle, outerAngle, innerAngleDeg, outerAngleDeg
    except:
        print("Not possible to calculate angles, will return (0,0)")
        traceback.print_exc()
        return 0,0,0,0

### finds the first pixel of the next line:
def findPixel(image):
    for ix in range(image.shape[0]-2, 1, -1):
        for iy in range(image.shape[1]-2, 1, -1):
            #print("ix: " + str(ix) + ", iy: " + str(iy) + ", image(ix,iy): " + str(image[ix,iy]))
            if image[ix,iy] < 0.5:
                image[ix,iy] = 1
                return ix,iy
    return False,False

### finds the next pixel in a line:
def findAdjacentPixel(image,ix,iy):
    ax=ix
    try:
        for ay in range(iy+1,iy-1,-1):
            print('ay',ay)
            if ax and ay:
                if image[ax,ay] < 0.5:
                    image[ax,ay] = 1
                    return ax,ay
                for ax in range(ix+1,ix-1,-1):
                    if image[ax,ay] < 0.5:
                        image[ax,ay] = 1
                        return ax,ay
        for ay in range(iy-1,iy+1,1):
            if ax and ay:
                if image[ax,ay] < 0.5:
                    image[ax,ay] = 1
                    return ax,ay
        return False,False
    except:
        print("something went wrong")
        return False,False

### calculate the angles of the two servos:
def getAngles2(image, arms):
    try:
        r_2 = image['currentX']**2 + image['currentY']**2
        l_sq = arms['innerArmLength']**2 + arms['outerArmLength']**2
        term2 = (r_2 - l_sq)/(2*arms['innerArmLength']*arms['outerArmLength'])
        term1 = ((1 - term2**2)**0.5)*-1
        # calculate outer angle
        arms['outerArmAngle'] = math.atan2(term1, term2)
        k1 = arms['innerArmLength'] + arms['outerArmLength']*math.cos(arms['outerArmAngle'])
        k2 = arms['outerArmLength']*math.sin(arms['outerArmAngle'])
        r  = (k1**2 + k2**2)**0.5
        gamma = math.atan2(k2,k1)
        # calculate inner angle
        arms['innerArmAngle'] = math.atan2(image['currentY'],image['currentX']) - gamma
        # outer angle seems to be always negative, therefore add 180°:
        arms['outerArmAngle'] += math.pi
        arms['innerArmAngleDeg'] = math.degrees(arms['innerArmAngle'])
        arms['outerArmAngleDeg'] = math.degrees(arms['outerArmAngle'])
        # return angles, since outer angle is always negative, shift it by 180°
        return
    except:
        print("Not possible to calculate angles, will return (0,0)")
        arms['outerArmAngle'] = arms['outerArmAngleDeg'] = arms['innerArmAngle'] = arms['innerArmAngleDeg'] = 0
        traceback.print_exc()
        return

### finds the first pixel of the next line:
def findPixel2(image):
    for ix in range(image['array'].shape[0]-1, 2, -1):
        for iy in range(image['array'].shape[1]-1, 2, -1):
            if image['array'][ix,iy] < 0.5:
                image['array'][ix,iy] = 1
                image['foundNextPixel'] = True
                image['currentXInArray'] = ix
                image['currentYInArray'] = iy
                print('ix, iy, arrayIXIY:', image['currentXInArray'], image['currentYInArray'], image['array'][ix,iy])
                return
    image['foundNextPixel'] = False
    print('222ix, iy, arrayIXIY:', ix, iy, image['array'][ix,iy])
    return

### finds the next pixel in a line:
def findAdjacentPixel2(image):
    ax=image['currentXInArray']
    for ay in range(image['currentYInArray']+1,image['currentYInArray']-2,-1):
        if image['array'][ax,ay] < 0.5:
            image['array'][ax,ay] = 1
            image['foundNextPixel'] = True
            image['currentXInArray'] = ax
            image['currentYInArray'] = ay
            return
        for ax in range(image['currentXInArray']+1,image['currentXInArray']-2,-1):
            if image['array'][ax,ay] < 0.5:
                image['array'][ax,ay] = 1
                image['foundNextPixel'] = True
                image['currentXInArray'] = ax
                image['currentYInArray'] = ay
                return
    for ay in range(image['currentYInArray']-1,image['currentYInArray']+2,1):
        if image['array'][ax,ay] < 0.5:
            image['array'][ax,ay] = 1
            image['foundNextPixel'] = True
            image['currentXInArray'] = ax
            image['currentYInArray'] = ay
            return
    image['foundNextPixel'] = False
    return
