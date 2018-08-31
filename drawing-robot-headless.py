
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
drawing-robot-headless
invoke with 'bokeh serve --show drawing-robot-headless' and open in browser (localhost:5006)
"""

### libraries
# external
import configparser # for importing config file
import bokeh.plotting as bp
from bokeh.io import curdoc
from bokeh.models import Panel, Button
from bokeh.models.widgets import Tabs, Div, TextInput, MultiSelect
from bokeh.layouts import column, row, WidgetBox
from time import sleep
# own stuff:
from helper import *
from imageProcessor.imageProcessor import *
from simulator.simulator import *
#from raspiRobot.raspiRobot import *

### reading variables from config file:
config = configparser.ConfigParser()
# config.optionxform = lambda option: option # otherwise its lowercase only <- don't need?
config.read('config.ini')
# general:
debug = config['general'].getboolean('debug')
originX = config['general'].getint('originX')
originY = config['general'].getint('originY')
imageScaleFactor = config['general'].getint('imageScale')
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
waitTimeFar = config['raspi'].getfloat('waitTimeFar')
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
            'innerArmActuationRange':innerArmActuationRange, 'innerArmMinPulse':innerArmMinPulse, 'innerArmMaxPulse':innerArmMaxPulse,
       'outerArmLength':outerArmLength, 'outerArmAngleRad':0, 'innerArmAngleDeg':0, 'outerArmChannel':outerArmChannel,
            'outerArmActuationRange':outerArmActuationRange, 'outerArmMinPulse':outerArmMinPulse, 'outerArmMaxPulse':outerArmMaxPulse,
       'penUpAngle':penUpAngle, 'penDownAngle':penDownAngle,'penChannel':penChannel,
       'armLength': innerArmLength + outerArmLength}

image = {'inputFilename':"", 'outputFilename':outputFilename, 'treshold':treshold,
         'originX':originX, 'originY':originY, 'edgeAlgorithm':edgeAlgorithm,
         'lineCounter':0, 'pixelCounter':0, 'currentLineX':[], 'currentLineY':[],
         'skipProcessing':skipProcessing, 'foundNextPixel':True, 'foundLastPixel':False}

raspi = {'switchedOn':raspiSwitchedOn, 'frequency':frequency, 'waitTimeNear':waitTimeNear, 'waitTimeFar':waitTimeFar, 'waitTimePen':waitTimePen}

simulation = {'switchedOn':simulatorSwitchedOn, 'browser':browser, 'sizeX':sizeX, 'sizeY':sizeY,
              'penWidth':penWidth, 'penColor':penColor, 'animateArms':animateArms,'lines':[]}

allback_id = None

### parts of browser window:
# info tab:
def settingsTab():
    header = Div(text="""<h2>Settings</h2></br><h3>Robot</h3>""")
    headerSimulator = Div(text="""<h3>Simulator</h3>""")
    headerImage = Div(text="""<h3>Image</h3>""")

    # include checkbox for on/off
    settingsInnerArmLength = TextInput(value=str(arms['innerArmLength']), title="Inner arm length:")
    settingsInnerArmMinPulse= TextInput(value=str(arms['innerArmMinPulse']), title="Inner arm mininum pulse:")
    settingsInnerArmMaxPulse= TextInput(value=str(arms['innerArmMaxPulse']), title="Inner arm maximum pulse:")
    settingsInnerArmActuationRange= TextInput(value=str(arms['innerArmActuationRange']), title="Inner arm actuation range:")
    settingsOuterArmLength = TextInput(value=str(arms['outerArmLength']), title="Outer arm length:")
    settingsOuterArmMinPulse= TextInput(value=str(arms['outerArmMinPulse']), title="Outer arm mininum pulse:")
    settingsOuterArmMaxPulse= TextInput(value=str(arms['outerArmMaxPulse']), title="Outer arm maximum pulse:")
    settingsOuterArmActuationRange= TextInput(value=str(arms['outerArmActuationRange']), title="Outer arm actuation range:")
    settingsPenUpAngle= TextInput(value=str(arms['penUpAngle']), title="Angle for pen up:")
    settingsPenDownAngle= TextInput(value=str(arms['penDownAngle']), title="Angle for pen down:")
    settingsWaitTimeNear= TextInput(value=str(raspi['waitTimeNear']), title="Wait time if next pixel is near:")
    settingsWaitTimeFar= TextInput(value=str(raspi['waitTimeFar']), title="Wait time if next pixel is far:")
    settingsWaitTimePen= TextInput(value=str(raspi['waitTimePen']), title="Wait time after pen movement:")

    settingsImageScale = TextInput(value=str(imageScaleFactor), title="Image scale:")
    settingsUpdate = Button(label='Update settings', width=200)
    settingsUpdateConfig = Button(label='Update settings and write to config', width=200)
    settingsReadConfig = Button(label='Read settings from config', width=200)

    settingsOutputFilename = TextInput(value=str(image['outputFilename']), title="Filename of output file:")
    settingsInputFilename = TextInput(value=str(image['inputFilename']), title="Filename of input file:")
    settingsTreshold = TextInput(value=str(image['treshold']), title="Threshold for conversion to black and white image:")
    settingsOriginX = TextInput(value=str(image['originX']), title="Origin x:")
    settingsOriginY = TextInput(value=str(image['originY']), title="Origin y:")
    settingsEdgeAlgorithm = MultiSelect(value=[str(image['edgeAlgorithm'])], title="Edgde detection algorithm:",
                                        options=['scharr','frangi','canny'])

    #include checkbox for on/off
    settingsBrowser = TextInput(value=str(simulation['browser']), title="Browser used:")
    settingsPenWidth = TextInput(value=str(simulation['penWidth']), title="Width of pen:")
    settingsPenColor = TextInput(value=str(simulation['penColor']), title="Color of pen:")
    settingsSizeX = TextInput(value=str(simulation['sizeX']), title="Width of simulation window:")
    settingsSizeY = TextInput(value=str(simulation['sizeY']), title="Height of simulation window:")
    #include checkbox for animate arms
    #button.on_click(startButton)
    info = column(header,
                  row(settingsInnerArmLength, settingsInnerArmActuationRange),
                  row(settingsInnerArmMinPulse, settingsInnerArmMaxPulse),
                  row(settingsOuterArmLength, settingsOuterArmActuationRange),
                  row(settingsOuterArmMinPulse, settingsOuterArmMaxPulse),
                  row(settingsPenUpAngle, settingsPenDownAngle),
                  row(settingsWaitTimeNear, settingsWaitTimeFar),
                  settingsWaitTimePen,
                  headerImage,
                  row(settingsInputFilename, settingsOutputFilename),
                  row(settingsOriginX, settingsOriginY),
                  row(settingsEdgeAlgorithm,settingsTreshold),
                  headerSimulator,
                  row(settingsSizeX,settingsSizeY),
                  row(settingsPenWidth,settingsPenColor),
                  settingsBrowser,
                  row(settingsReadConfig,settingsUpdate,settingsUpdateConfig))
    #show(widgetbox(div))
    settings = Panel(child = info, title = "Settings")
    return settings

# Image manipulation tab1
def imageTab():
    info = Div(text="""insert image manipulation magic here!""")
    tabImage = Panel(child = info, title = "Image processing")
    return tabImage

# RasPi tab
def loggingTab():
    info = Div(text="""Here some logging information will be displayed""")
    tabRaspi = Panel(child = info, title = "Logging informations")
    return tabRaspi

### what to do if start button is clicked:
def startButton():
    global callback_id
    if button.label == '► Start':
        button.label = '❚❚ Stop'
        callback_id = curdoc().add_periodic_callback(update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

### drawing function
def drawLine(image, arms, raspi):
    findPixel(image) # looking for the first pixel in image, sets image['foundNextPixel']
    if image['foundNextPixel']:
        image['lineCounter'] += 1 # linecounter +1
        getAngles(image, arms) # calculate angles of robot arms
        if arms['innerArmAngleDeg'] != 0 and arms['outerArmAngleDeg'] != 0:
            if simulation['switchedOn']:
                newLine(simulation, image)
                if simulation['animateArms']:
                    moveArms(arms, simulation)
            if raspi['switchedOn']:
                image['distance'] = "far"
                raspiRobot.raspiRobot.setAngle(arms,image)
                raspiRobot.raspiRobot.movePen(down, raspi['waitTimePen'])
            findAdjacentPixel(image)
            if (not image['foundNextPixel']) and simulation['switchedOn']:
                drawPixel(simulation, image)
            while image['foundNextPixel']:
                getAngles(image, arms)
                if arms['innerArmAngleDeg'] != 0 and arms['outerArmAngleDeg'] != 0:
                    if simulation['switchedOn']:
                        image['currentLineX'].append(image['currentX'])
                        image['currentLineY'].append(image['currentY'])
                        if simulation['animateArms']:
                            moveArms(arms, simulation)
                        appendLine(simulation, image)
                    if raspi['switchedOn']:
                        image['distance'] = "near"
                        raspiRobot.raspiRobot.setAngle(arms,image)
                    findAdjacentPixel(image)
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
image['array'] = imageAsArray(image['outputFilename'], image['treshold'])
image['scale'] = float(imageScaleFactor) * float(image['array'].shape[0]) / float(arms['armLength'])
image['width'] = image['array'].shape[0]/image['scale']
image['height'] = image['array'].shape[1]/image['scale']
image['currentXInArray'] = image['currentYInArray'] = False

### behaviour of start button:
button = Button(label='► Start', width=60)
button.on_click(startButton)

### setting up the browser window
tab1 = imageTab()
tab2 = settingsTab()
tab3 = setupSimulation(simulation, image, arms)
tab4 = loggingTab()
tabs = Tabs(tabs = [tab2, tab1, tab3, tab4])
curdoc().add_root(column(children=[button, tabs], sizing_mode='scale_width', name='mainLayout'))
#curdoc().add_root(column(children=[header, tabs], sizing_mode='scale_width', name='mainLayout'))
### drawing process starts here:
#curdoc().add_periodic_callback(update, 1000)

#test()
