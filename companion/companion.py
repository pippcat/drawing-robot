#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import image_manipulator
import drawing_simulator

print("Drawing Robot Companion Program")
print("===============================\n")

def process_image():
    imagename = input("Please put your image into the images subfolder and enter the filename with extension but without path here: ")
    im = image_manipulator.open_image(imagename)
    res = image_manipulator.resize_image(im, 800)
    edge = image_manipulator.edge_detector(res)
    inv = image_manipulator.inverter(edge)
    image_manipulator.save_file('out', inv)
    image_manipulator.show_results(im, res, edge, inv)

def draw_simulation():
    scenery = drawing_simulator.setup_scenery()
    drawing_simulator.dummy(scenery['angleLabel'], scenery['innerArm'], scenery['outerArm'], scenery['innerLength'],scenery['outerLength'])

draw_simulation()
