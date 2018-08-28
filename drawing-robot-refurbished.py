#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# external libraries:
from dialog import Dialog
from datetime import datetime
from subprocess import call
import configparser # for importing config file
import os
import sys
import math

# own stuff:
import helper
import imageProcessor.imageProcessor
import simulator.newsimulator

### importing config.ini:
config = configparser.ConfigParser()
config.optionxform = lambda option: option # otherwise its lowercase only
config.read(os.getcwd() + '/config.ini')

### reading variables from config file:
# general:
debug = config['GENERAL'].getboolean('debug')
innerArmLength = config['GENERAL']['innerArmLength']
outerArmLength = config['GENERAL']['outerArmLength']
originX = config['GENERAL']['originX']
originY = config['GENERAL']['originY']
imageScale = config['GENERAL']['imageScale']
# simulator:
browser = config['SIMULATOR']['browser']
sizeX = config['SIMULATOR'].getint('sizeX')
sizeY = config['SIMULATOR'].getint('sizeY')

d = Dialog(dialog='dialog', autowidgetsize=True)
d.set_background_title("Drawing Robot V0.1")

def menu():
    os.system('python3 drawing-robot-refurbished.py')

def imageProcessor():
    print("image processor")

def drawingSimulator():
    d.msgbox("drawing simulator", width=40, height=10)
    simulator.newsimulator.setupSimulation(browser, sizeX, sizeY, innerArmLength, outerArmLength, originX, originY, imageScale)
    return

def arduinoRobot():
    print("arduino robot")

def raspiRobot():
    print("raspi robot")

def quit():
    sys.exit(0)

def changeSettings():
    d.msgbox("change settings")
    return

def showSettings():
    d.textbox('config.ini')
    return

menu_items = [
    ('Show settings', 'Show Settings', showSettings),
    ('Change settings', 'Change Settings', changeSettings),
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
