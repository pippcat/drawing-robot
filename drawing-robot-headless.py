#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# external libraries:
from datetime import datetime
from subprocess import call
from random import random
import configparser # for importing config file
import os
import sys
import math

# own stuff:
import helper
import imageProcessor.imageProcessor
import simulator.newsimulator

import bokeh.plotting as bp
from bokeh.io import curdoc
from bokeh.models import Panel, Button
from bokeh.models.widgets import Tabs, Div, TextInput
from bokeh.layouts import column, row, WidgetBox

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

### header
def header():
    header = Div(text="""<h1>Drawing Robot</h1>Version 0.1""")
    return header

### info tab:
def settingsTab():
    header = Div(text="""<h2>Settings</h2></br><h3>General</h3>""")
    headerSimulator = Div(text="""
    <h3>Simulator</h3>
    <h3>RaspberryPi</h3>
    </br>Insert config file here!""")
    settingsInnerArmLength = TextInput(value=innerArmLength, title="Inner arm length:")
    settingsOuterArmLength = TextInput(value=outerArmLength, title="Outer arm length:")
    settingsOriginX = TextInput(value=originX, title="Origin x:")
    settingsOriginY = TextInput(value=originY, title="Origin y:")
    settingsImageScale = TextInput(value=imageScale, title="Image scale:")
    info = column(header, row(settingsInnerArmLength, settingsOuterArmLength), row(settingsOriginX, settingsOriginY), settingsImageScale, headerSimulator)
    #show(widgetbox(div))
    settings = Panel(child = info, title = "Settings")
    return settings

### RasPi tab
def infoRaspi():
    info = Div(text="""Here some information about the Raspi will be displayed""")
    tabRaspi = Panel(child = info, title = "RaspberryPi Info")
    return tabRaspi

### setting up the browser window
header = header()
tab1 = settingsTab()
tab2 = simulator.newsimulator.setupSimulation(browser, sizeX, sizeY, innerArmLength, outerArmLength, originX, originY, imageScale)
tab3 = infoRaspi()
tabs = Tabs(tabs = [tab1, tab2, tab3])




curdoc().add_root(column(header, tabs))

#bp.show(column(header, tabs), browser=browser)
