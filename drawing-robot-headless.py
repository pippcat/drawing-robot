
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
from time import sleep
# own stuff:
import helper
import imageProcessor.imageProcessor
import simulator.newsimulator
#import raspiRobot.raspiRobot

### reading variables from config file:
config = configparser.ConfigParser()
# config.optionxform = lambda option: option # otherwise its lowercase only <- don't need?
config.read('config.ini')
# general:
debug = config['general'].getboolean('debug')
originX = config['general'].getint('originX')
originY = config['general'].getint('originY')
imageScaleFactor = config['general'].getint('imageScale')
print(imageScaleFactor)
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
raspiSwitchedOn = config['raspi'].getboolean('switchedOn')
frequency = config['raspi'].getint('frequency')
waitTimeNear = config['raspi'].getfloat('waitTimeNear')
waitTimeNew = config['raspi'].getfloat('waitTimeNew')
waitTimePen = config['raspi'].getfloat('waitTimePen')
# simulator
simulatorSwitchedOn = config['simulator'].getboolean('switchedOn')
browser = config['simulator']['browser']
sizeX = config['simulator'].getint('sizeX')
sizeY = config['simulator'].getint('sizeY')
penWidth = config['simulator'].getint('penWidth')
penColor = config['simulator']['penColor']
animateArms = config['simulator'].getboolean('animateArms')

### setting up some meaningful dictionaries:
arms = {'innerArmLength':innerArmLength, 'innerArmAngleRad':0, 'innerArmAngleDeg':0, 'innerArmChannel':innerArmChannel,
            'innerArmActuationRange':innerArmActuationRange, 'innerArmMinPulse':innerArmMinPulse,
       'outerArmLength':outerArmLength, 'outerArmAngleRad':0, 'innerArmAngleDeg':0, 'outerArmChannel':outerArmChannel,
            'outerArmActuationRange':outerArmActuationRange, 'outerArmMinPulse':outerArmMinPulse,
       'penUpAngle':penUpAngle, 'penDownAngle':penDownAngle,'penChannel':penChannel,
       'armLength': innerArmLength + outerArmLength}

image = {'inputFilename':"", 'outputFilename':outputFilename, 'treshold':treshold,
         'originX':originX, 'originY':originY, 'edgeAlgorithm':edgeAlgorithm,
         'lineCounter':0, 'pixelCounter':0, 'currentLineX':[], 'currentLineY':[],
         'skipProcessing':skipProcessing, 'foundNextPixel':True, 'foundLastPixel':False}

raspi = {'switchedOn':raspiSwitchedOn, 'frequency':frequency, 'waitTimeNear':waitTimeNear, 'waitTimeNew':waitTimeNew, 'waitTimePen':waitTimePen}

simulation = {'switchedOn':simulatorSwitchedOn, 'browser':browser, 'sizeX':sizeX, 'sizeY':sizeY,
              'penWidth':penWidth, 'penColor':penColor, 'animateArms':animateArms,'lines':[]}

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
    settingsImageScale = TextInput(value=str(imageScaleFactor), title="Image scale:")
    info = column(header, row(settingsInnerArmLength, settingsOuterArmLength), row(settingsOriginX, settingsOriginY), settingsImageScale, headerSimulator)
    #show(widgetbox(div))
    settings = Panel(child = info, title = "Settings")
    return settings
# RasPi tab
def infoRaspi():
    info = Div(text="""Here some information about the Raspi will be displayed""")
    tabRaspi = Panel(child = info, title = "RaspberryPi Info")
    return tabRaspi

### drawing function
def drawLine(image, arms, raspi):
    helper.findPixel(image) # looking for the first pixel in image, sets image['foundNextPixel']
    if image['foundNextPixel']:
        image['lineCounter'] += 1 # linecounter +1
        helper.getAngles(image, arms) # calculate angles of robot arms
        if arms['innerArmAngleDeg'] != 0 and arms['outerArmAngleDeg'] != 0:
            if simulation['switchedOn']:
                simulator.newsimulator.newLine(simulation, image)
                if simulation['animateArms']:
                    simulator.newsimulator.moveArms(arms, simulation)
            if raspi['switchedOn']:
                image['distance'] = "far"
                raspiRobot.raspiRobot.setAngle(arms,image)
                raspiRobot.raspiRobot.movePen(down, raspi['waitTimePen'])
            helper.findAdjacentPixel(image)
            if (not image['foundNextPixel']) and simulation['switchedOn']:
                simulator.newsimulator.drawPixel(simulation, image)
            while image['foundNextPixel']:
                helper.getAngles(image, arms)
                if arms['innerArmAngleDeg'] != 0 and arms['outerArmAngleDeg'] != 0:
                    if simulation['switchedOn']:
                        image['currentLineX'].append(image['currentX'])
                        image['currentLineY'].append(image['currentY'])
                        if simulation['animateArms']:
                            simulator.newsimulator.moveArms(arms, simulation)
                        simulator.newsimulator.appendLine(simulation, image)
                    if raspi['switchedOn']:
                        image['distance'] = "near"
                        raspiRobot.raspiRobot.setAngle(arms,image)
                    helper.findAdjacentPixel(image)
    else:
        # hurray, we finished drawing
        print('Done drawing ', image['pixelCounter'], ' pixel in ', image['lineCounter'], 'lines.')
        # delete variables in dictionary:
        image['currentX'] = image['currentY'] = image['currentXInArray'] = image['currentYInArray'] = False
        image['currentLineX'] = image['currentLineY'] = []
        return

### what to be one once the browser window is updated:
def update():
    drawLine(image, arms, raspi)
    if raspi['switchedOn']:
        raspiRobot.raspiRobot.movePen(up, raspi['waitTimePen'])

def test():
    # setup everything and draw the first line
    update()

### populating image dictionary:
image['array'] = imageProcessor.imageProcessor.imageAsArray(image['outputFilename'], image['treshold'])
image['scale'] = float(imageScaleFactor) * float(image['array'].shape[0]) / float(arms['armLength'])
image['width'] = image['array'].shape[0]/image['scale']
image['height'] = image['array'].shape[1]/image['scale']
image['currentXInArray'] = image['currentYInArray'] = False


### setting up the browser window
header = header()
tab1 = settingsTab()
tab2 = simulator.newsimulator.setupSimulation(simulation, image, arms)
tab3 = infoRaspi()
tabs = Tabs(tabs = [tab2, tab1, tab3])
curdoc().add_root(column(children=[header, tabs], sizing_mode='scale_width', name='mainLayout'))
### drawing process starts here:
curdoc().add_periodic_callback(update, 1000)

#test()
