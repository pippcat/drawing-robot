#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
drawing-robot-headless

invoke with 'bokeh serve drawing-robot-headless' and open in browser (localhost:5006)
"""

### libraries
# external
import configparser # for importing config file
import bokeh.plotting as bp
from bokeh.io import curdoc
from bokeh.models import Panel, Button
from bokeh.models.widgets import Tabs, Div, TextInput
from bokeh.layouts import column, row, WidgetBox
# own stuff:
import helper
import imageProcessor.imageProcessor
import simulator.newsimulator

### reading variables from config file:
config = configparser.ConfigParser()
# config.optionxform = lambda option: option # otherwise its lowercase only <- don't need?
config.read('config.ini')
# general:
debug = config['general'].getboolean('debug')
originX = config['general'].getint('originX')
originY = config['general'].getint('originY')
imageScale = config['general'].getint('imageScale')
# arms:
innerArmLength = config['arms'].getint('innerArmLength')
innerArmChannel = config['arms'].getint('innerArmChannel')
innerArmActuationRange = config['arms'].getint('innerArmActuationRange')
innerArmMinPulse = config['arms'].getint('innerArmMinPulse')
innerArmMaxPulse = config['arms'].getint('innerArmMaxPulse')
outerArmLength = config['arms'].getint('outerArmLength')
outerArmChannel = config['arms'].getint('outerArmChannel')
outerArmActuationRange = config['arms'].getint('outerArmActuationRange')
outerArmMinPulse = config['arms'].getint('outerArmMinPulse')
outerArmMaxPulse = config['arms'].getint('outerArmMaxPulse')
penChannel = config['arms'].getint('penMotorChannel')
penUpAngle = config['arms'].getint('penMotorUpAngle')
penDownAngle = config['arms'].getint('penMotorDownAngle')
# imageprocessor
edgeAlgorithm = config['imageprocessor']['edgeAlgorithm']
skipProcessing = config['imageprocessor'].getboolean('skipProcessing')
outputFilename = config['imageprocessor']['outputFilename']
treshold = config['imageprocessor'].getfloat('treshold')
# raspi
frequency = config['raspi'].getint('frequency')
waitTimeNear = config['raspi'].getfloat('waitTimeNear')
waitTimeNew = config['raspi'].getfloat('waitTimeNew')
waitTimePen = config['raspi'].getfloat('waitTimePen')
# simulator
browser = config['simulator']['browser']
sizeX = config['simulator'].getint('sizeX')
sizeY = config['simulator'].getint('sizeY')

### setting up some meaningful dictionaries:
arms = {'innerArmLength':innerArmLength, 'innerArmAngle':0, 'innerArmCHannel':innerArmChannel,
            'innerArmActuationRange':innerArmActuationRange, 'innerArmMinPulse':innerArmMinPulse,
       'outerArmLength':outerArmLength, 'outerAngle':0, 'outerArmCHannel':outerArmChannel,
            'outerArmActuationRange':outerArmActuationRange, 'outerArmMinPulse':outerArmMinPulse,
       'penUpAngle':penUpAngle, 'penDownAngle':penDownAngle,'penChannel':penChannel,
       'armLength': innerArmLength + outerArmLength}

image = {'inputFilename':"", 'outputFilename':outputFilename, 'scale':imageScale,
         'originX':originX, 'originY':originY, 'edgeAlgorithm':edgeAlgorithm,
         'treshold':treshold,'skipProcessing':skipProcessing}

raspi = {'frequency':frequency, 'waitTimeNear':waitTimeNear, 'waitTimeNew':waitTimeNew, 'waitTimePen':waitTimePen}

simulation = {'browser':browser, 'sizeX':sizeX, 'sizeY':sizeY}

### parts of browser window:
# header
def header(): # header
    header = Div(text="""""")
    #header = Div(text="""<h1>Drawing Robot</h1>""")
    return header
# info tab:
def settingsTab():
    header = Div(text="""<h2>Settings</h2></br><h3>General</h3>""")
    headerSimulator = Div(text="""
    <h3>Simulator</h3>
    <h3>RaspberryPi</h3>
    </br>Insert config file here!""")
    settingsInnerArmLength = TextInput(value=str(arms['innerArmLength']), title="Inner arm length:")
    settingsOuterArmLength = TextInput(value=str(outerArmLength), title="Outer arm length:")
    settingsOriginX = TextInput(value=str(originX), title="Origin x:")
    settingsOriginY = TextInput(value=str(originY), title="Origin y:")
    settingsImageScale = TextInput(value=str(imageScale), title="Image scale:")
    info = column(header, row(settingsInnerArmLength, settingsOuterArmLength), row(settingsOriginX, settingsOriginY), settingsImageScale, headerSimulator)
    #show(widgetbox(div))
    settings = Panel(child = info, title = "Settings")
    return settings
# RasPi tab
def infoRaspi():
    info = Div(text="""Here some information about the Raspi will be displayed""")
    tabRaspi = Panel(child = info, title = "RaspberryPi Info")
    return tabRaspi

### populating image dictionary:
image['array'] = imageProcessor.imageProcessor.imageAsArray(image['outputFilename'], image['treshold'])
image['width'] = image['array'].shape[0]/image['scale']
image['height'] = image['array'].shape[1]/image['scale']

### setting up the browser window
header = header()
tab1 = settingsTab()
tab2 = simulator.newsimulator.setupSimulation(simulation, image, arms)
tab3 = infoRaspi()
tabs = Tabs(tabs = [tab2, tab1, tab3])
curdoc().add_root(column(children=[header, tabs], sizing_mode='scale_width'))
