#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# shared helper functions for simulator and robots

import traceback
import math

def get_angles(image, arms):
    '''calculates the angles of the two servos'''
    try:
        r_2 = image['currentX']**2 + image['currentY']**2
        l_sq = arms['innerArmLength']**2 + arms['outerArmLength']**2
        term2 = (r_2 - l_sq)/(2*arms['innerArmLength']*arms['outerArmLength'])
        term1 = ((1 - term2**2)**0.5)*-1
        # calculate outer angle
        arms['outerArmAngleRad'] = math.atan2(term1, term2)
        k1 = arms['innerArmLength'] + arms['outerArmLength']*math.cos(arms['outerArmAngleRad'])
        k2 = arms['outerArmLength']*math.sin(arms['outerArmAngleRad'])
        r  = (k1**2 + k2**2)**0.5
        gamma = math.atan2(k2,k1)
        # calculate inner angle
        arms['innerArmAngleRad'] = math.atan2(image['currentY'],image['currentX']) - gamma
        # outer angle seems to be always negative, therefore add 180°:
        arms['outerArmAngleRad'] += math.pi
        arms['innerArmAngleDeg'] = math.degrees(arms['innerArmAngleRad'])
        arms['outerArmAngleDeg'] = math.degrees(arms['outerArmAngleRad'])
        # return angles, since outer angle is always negative, shift it by 180°
        return
    except:
        logging.warning("Not possible to calculate angles, will return (0,0)")
        arms['outerArmAngleRad'] = arms['outerArmAngleDeg'] = arms['innerArmAngleRad'] = arms['innerArmAngleDeg'] = 0
        traceback.print_exc()
        return

def find_pixel(image):
    '''finds the first pixel of the next line'''
    for ix in range(image['array'].shape[0]-1, 0, -1):
        for iy in range(image['array'].shape[1]-1, 0, -1):
            if image['array'][ix,iy] < 0.5:
                image['pixelCounter'] += 1
                image['array'][ix,iy] = 1
                image['foundNextPixel'] = True
                image['currentXInArray'] = ix
                image['currentYInArray'] = iy
                image['currentX'] = image['currentXInArray']/image['scale']+image['originX']
                image['currentY'] = image['currentYInArray']/image['scale']+image['originY']
                return
    image['foundLastPixel'] = True
    return

def find_adjacent_pixel(image):
    '''finds the next pixel in a line'''
    ax=image['currentXInArray']
    for ay in range(image['currentYInArray']+1,image['currentYInArray']-2,-1):
        if image['array'][ax,ay] < 0.5:
            image['pixelCounter'] += 1
            image['array'][ax,ay] = 1
            image['foundNextPixel'] = True
            image['currentXInArray'] = ax
            image['currentYInArray'] = ay
            image['currentX'] = image['currentXInArray']/image['scale']+image['originX']
            image['currentY'] = image['currentYInArray']/image['scale']+image['originY']
            return
        for ax in range(image['currentXInArray']+1,image['currentXInArray']-2,-1):
            if image['array'][ax,ay] < 0.5:
                image['pixelCounter'] += 1
                image['array'][ax,ay] = 1
                image['foundNextPixel'] = True
                image['currentXInArray'] = ax
                image['currentYInArray'] = ay
                image['currentX'] = image['currentXInArray']/image['scale']+image['originX']
                image['currentY'] = image['currentYInArray']/image['scale']+image['originY']
                return
    for ay in range(image['currentYInArray']-1,image['currentYInArray']+2,1):
        if image['array'][ax,ay] < 0.5:
            image['pixelCounter'] += 1
            image['array'][ax,ay] = 1
            image['foundNextPixel'] = True
            image['currentXInArray'] = ax
            image['currentYInArray'] = ay
            image['currentX'] = image['currentXInArray']/image['scale']+image['originX']
            image['currentY'] = image['currentYInArray']/image['scale']+image['originY']
            return
    image['foundNextPixel'] = False
    return
