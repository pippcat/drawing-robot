#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# external libraries:
from dialog import Dialog
from datetime import datetime
from subprocess import call
import os
import sys
import math

# own stuff:
import helper
import imageProcessor.imageProcessor

d = Dialog(dialog='dialog', autowidgetsize=True)

def menu():
    os.system('python3 drawing-robot-refurbished.py')

def imageProcessor():
    print("image processor")

def drawingSimulator():
    print("drawing simulator")

def arduinoRobot():
    print("arduino robot")

def raspiRobot():
    print("raspi robot")

def quit():
    sys.exit(0)

menu_items = [
    ('Process image', 'Process image to be compatible with simulator or robot', imageProcessor),
    ('Simulator', 'Use simulator to see what will be drawn', drawingSimulator),
    ('Arduino robot', 'Use arduino connected to laptop to draw image', arduinoRobot),
    ('RasPi robot', 'Use a RaspberryPi in same LAN to draw image', raspiRobot),
    ('Quit', 'Quit program', quit)
]

while True:
    choice = d.menu("What do you want to do?", choices=[i[0:2] for i in menu_items])
    os.system('clear')
    if choice[0] == Dialog.OK:
        func = next(m[2] for m in menu_items if m[0] == choice[1])
        func()
    else:
        menu()
