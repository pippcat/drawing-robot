#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# drawing robot companion app, can modify images and run the simulator

import image_manipulator
import drawing_simulator
import numpy as np

print("Drawing Robot Companion Program")
print("===============================\n")

def process_image():
    imagename = input("Please put your image into the images subfolder and enter the filename with extension but without path here: ")
    imagewidth = input("Which width in pixel should the processed image have (recommendation: 50 .. 100)? ")
    im = image_manipulator.open_image(imagename) # open image
    res = image_manipulator.resize_image(im, int(imagewidth)) # resize it
    edge = image_manipulator.edge_detector(res) # detect edges
    inv = image_manipulator.inverter(edge) # invert result
    image_manipulator.save_file('out', inv) # save file
    image_manipulator.show_results(im, res, edge, inv) # show results
    image = image_manipulator.image_as_array('out.png', 0.8) # store as array
    return image

def draw_simulation(image):
    print("setting up simulator")
    scenery = drawing_simulator.setup_scenery(image) # drawing the scenery
    drawing_simulator.draw_image(scenery['alphaLabel'], scenery['betaLabel'], scenery['innerArmLabel'], scenery['outerArmLabel'],scenery['innerArm'], scenery['outerArm'], scenery['innerLength'],scenery['outerLength'],scenery['image'], scenery['image_scale']) # draw the image

image = process_image() # either ..
#print("skipping image processing") # ..or:
#image = image_manipulator.image_as_array('out.png', 0.9)
draw_simulation(image)
