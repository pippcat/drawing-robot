
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
drawing-robot-headless
invoke with 'bokeh serve --show drawing-robot-headless' and open in browser (localhost:5006)
"""

### libraries
# external
import string
from random import choice
import pandas as pd
from bokeh.models import ColumnDataSource, CustomJS
import configparser # for importing config file
import bokeh.plotting as bp
from bokeh.events import ButtonClick
from bokeh.io import curdoc
from bokeh.models import Panel, Button, Range1d, Plot
from bokeh.models.widgets import Tabs, Div, TextInput, Select, Slider, PreText
from bokeh.layouts import column, row, WidgetBox
from time import sleep
# own stuff:
#from fileUpload import *
from helper import *
from imageProcessor.imageProcessor import *
from simulator.simulator import *
from raspiRobot.raspiRobot import *

from io import BytesIO
import base64
import os
import shutil
file_source = ColumnDataSource({'file_contents':[], 'file_name':[]})

### reading variables from config file:
config = configparser.ConfigParser()
# config.optionxform = lambda option: option # otherwise its lowercase only <- don't need?
config.read('drawing-robot/config.ini')
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
outputSize = config['imageprocessor'].getint('outputSize')
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
         'skipProcessing':skipProcessing, 'foundNextPixel':True, 'foundLastPixel':False,
         'outputSize':outputSize}

raspi = {'switchedOn':raspiSwitchedOn, 'frequency':frequency, 'waitTimeNear':waitTimeNear, 'waitTimeFar':waitTimeFar,
         'waitTimePen':waitTimePen, 'calibrateOuterArm': 0, 'calibrateInnerArm': 0, 'calibratePen': 0}

simulation = {'switchedOn':simulatorSwitchedOn, 'browser':browser, 'sizeX':sizeX, 'sizeY':sizeY,
              'penWidth':penWidth, 'penColor':penColor, 'animateArms':animateArms,'lines':[]}

callback_id = None

### parts of browser window:
# info tab:
def settingsTab():
    settingsElements = column(header,
                  row(settingsOriginX, settingsOriginY),
                  row(settingsInnerArmLength, settingsInnerArmActuationRange),
                  row(settingsInnerArmMinPulse, settingsInnerArmMaxPulse),
                  row(settingsOuterArmLength, settingsOuterArmActuationRange),
                  row(settingsOuterArmMinPulse, settingsOuterArmMaxPulse),
                  row(settingsPenUpAngle, settingsPenDownAngle),
                  row(settingsWaitTimeNear, settingsWaitTimeFar),
                  settingsWaitTimePen,
                  headerSimulator,
                  row(settingsSizeX,settingsSizeY),
                  row(settingsPenWidth,settingsPenColor),
                  settingsBrowser,
                  row(settingsReadConfig,settingsUpdate,settingsUpdateConfig))
    #show(widgetbox(div))
    settings = Panel(child = settingsElements, title = "Settings")
    return settings

def callbackSize():
    updateImageSettings()
    name = randomChar(2)
    im = openImage(image['inputFilename']) # open image
    saveFile(name + '_orig.png', im)
    res = resizeImage(im,image['outputSize']) # resize it
    saveFile(name + '_scaledown.png', res)
    edge = edgeDetector(res, image['edgeAlgorithm']) # detect edges
    saveFile(name + '_edge.png', edge)
    inv = inverter(edge) # invert result
    saveFile(name + '_inv.png', inv) # save file
    result = imageAsArray(name + '_inv.png', image['treshold']) # store as array
    image['array'] = result
    saveFile(name + '_result.png', result)
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_result.png']))
    #maybe this solves random name bug: ?
    #img_orig.data.update(dict(url = ['drawing-robot/static/' + name + '_orig.png']))
    showImageOrig.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_orig)
    showImageResize.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_scaledown)
    showImageEdge.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_edge)
    showImageInv.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_inv)
    showImageResult.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_result)
    image['outputFilename'] = name
    updateSimulationBackground(simulation, image)

def callbackTreshold():
    updateImageSettings()
    name = randomChar(2)
    im = openImage(image['outputFilename'] + '_inv.png') # open image
    saveFile(name + '_inv.png', im)
    result = imageAsArray(image['outputFilename'] + '_inv.png', image['treshold']) # store as array
    image['array'] = result
    #saveFile(image['outputFilename'] + '_result.png', result)
    saveFile(name + '_result.png', result)
    #img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' + image['outputFilename'] + '_result.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_result.png']))
    showImageResult.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(result.shape[0])*float(result.shape[1]),
        w=simulation['sizeX'],
        source=img_result)
    image['outputFilename'] = name
    updateSimulationBackground(simulation, image)

def callbackCalibrateOuterArmButton():
    raspi['calibrateOuterArm'] += 1
    if raspi['calibrateOuterArm'] == 1:
        calibrate(arms, raspi, "outerArm", 45)
        calibrateInfo.text = """outerArm moved to 45deg, check if angle is right and press button again!"""
    if raspi['calibrateOuterArm'] == 2:
        calibrate(arms, raspi, "outerArm", 90)
        calibrateInfo.text = """outerArm moved to 90deg, check if angle is right and press button again!"""
    if raspi['calibrateOuterArm'] == 3:
        calibrate(arms, raspi, "outerArm", 180)
        calibrateInfo.text = """outerArm moved to 180deg, check if angle is right and press button again!"""
    if raspi['calibrateOuterArm'] == 4:
        raspi['calibrateOuterArm'] = 0
        calibrate(arms, raspi, "outerArm", 90)
        calibrateInfo.text = """outerArm moved to 90deg, calibration procedure done.
Adjust outerArmMinPulse and outerArmMaxPulse
and redo procedure until angles are good!"""

def callbackCalibrateInnerArmButton():
        raspi['calibrateInnerArm'] += 1
        if raspi['calibrateInnerArm'] == 1:
            calibrate(arms, raspi, "innerArm", 0)
            calibrateInfo.text = """innerArm moved to 0deg, check if angle is right and press button again!"""
        if raspi['calibrateInnerArm'] == 2:
            calibrate(arms, raspi, "innerArm", 90)
            calibrateInfo.text = """innerArm moved to 90deg, check if angle is right and press button again!"""
        if raspi['calibrateInnerArm'] == 3:
            calibrate(arms, raspi, "innerArm", 180)
            calibrateInfo.text = """innerArm moved to 180deg, check if angle is right and press button again!"""
        if raspi['calibrateInnerArm'] == 4:
            raspi['calibrateInnerArm'] = 0
            calibrate(arms, raspi, "innerArm", 90)
            calibrateInfo.text = """innerArm moved to 90deg, calibration procedure done.
    Adjust innerArmMinPulse and innerArmMaxPulse
    and redo procedure until angles are good!"""

def callbackCalibratePenButton():
    raspi['calibratePen'] += 1
    if raspi['calibratePen'] == 1:
        calibrate(arms, raspi, "pen", 110, "down")
        calibrateInfo.text = """pen moved down, check if angle is right!"""
    if raspi['calibratePen'] == 2:
        calibrate(arms, raspi, "pen", 110, "up")
        calibrateInfo.text = """pen moved up, check if angle is right!"""
    if raspi['calibratePen'] == 3:
        raspi['calibratePen'] = 0

def callbackUpdateCalibration():
    arms['innerArmMinPulse'] = calibrateInnerArmMinPulseSlider.value
    arms['innerArmMaxPulse'] = calibrateInnerArmMaxPulseSlider.value
    arms['outerArmMinPulse'] = calibrateOuterArmMinPulseSlider.value
    arms['outerArmMaxPulse'] = calibrateOuterArmMaxPulseSlider.value
    arms['penDownAngle'] = calibratePenDownAngleSlider.value
    arms['penUpAngle'] = calibratePenUpAngleSlider.value
    calibrateInfo.text = """Calibration values updated!"""
    print(arms)

def callbackWriteConfig():
    print('config will be written now!')

def callbackAlgorithm():
    print('callback algorithm')
    updateImageSettings()
    name = randomChar(2)
    im = openImage(image['outputFilename'] + '_scaledown.png') # open image
    saveFile(name + '_scaledown.png', im)
    edge = edgeDetector(im, str(image['edgeAlgorithm'])) # detect edges
    saveFile(name + '_edge.png', edge)
    inv = inverter(edge) # invert result
    saveFile(name + '_inv.png', inv) # save file
    result = imageAsArray(name + '_inv.png', image['treshold']) # store as array
    image['array'] = result
    saveFile(name + '_result.png', result)
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_result.png']))
    img_orig.data.update(dict(url = ['drawing-robot/static/' + name + '_orig.png']))
    showImageOrig.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_orig)
    showImageResize.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_scaledown)
    showImageEdge.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_edge)
    showImageInv.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_inv)
    showImageResult.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_result)
    image['outputFilename'] = name
    updateSimulationBackground(simulation, image)


def callbackFile(attr,old,new):
    raw_contents = file_source.data['file_contents'][0]
    # remove the prefix that JS adds
    prefix, b64_contents = raw_contents.split(",", 1)
    file_contents = base64.b64decode(b64_contents)
    file_io = BytesIO(file_contents)
    filepath = 'drawing-robot/static/' + file_source.data['file_name'][-1]
    settingsInputFilename.update(value=file_source.data['file_name'][-1])
    with open(filepath, 'wb') as f:
        shutil.copyfileobj(file_io, f)
    image['inputFilename'] = settingsInputFilename.value
    updateImageSettings()
    #save settings before!
    name = randomChar(2)
    #name = image['inputFilename']
    print('Image name on hard disk:',name)
    im = openImage(image['inputFilename']) # open image
    saveFile(name + '_orig.png', im)
    res = resizeImage(im,image['outputSize']) # resize it
    saveFile(name + '_scaledown.png', res)
    edge = edgeDetector(res, str(image['edgeAlgorithm'])) # detect edges
    saveFile(name + '_edge.png', edge)
    inv = inverter(edge) # invert result
    saveFile(name + '_inv.png', inv) # save file
    result = imageAsArray(name + '_inv.png', image['treshold']) # store as array
    image['array'] = result
    saveFile(name + '_result.png', result)
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' + name + '_result.png']))
    img_orig.data.update(dict(url = ['drawing-robot/static/' + name + '_orig.png']))
    showImageOrig.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_orig)
    showImageResize.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_scaledown)
    showImageEdge.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_edge)
    showImageInv.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_inv)
    showImageResult.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(im.shape[0])*float(im.shape[1]),
        w=simulation['sizeX'],
        source=img_result)
    image['outputFilename'] = name
    updateSimulationBackground(simulation, image)

### what to do if start button is clicked:
def callbackStartButton():
    global callback_id
    if button.label == 'Start':
        button.label = 'Stop'
        button.button_type = 'warning'
        callback_id = curdoc().add_periodic_callback(update, 200)
    else:
        button.label = 'Start'
        button.button_type = 'success'
        curdoc().remove_periodic_callback(callback_id)

def callbackResetButton():
    print('reset does not work yet')

def updateImageSettings():
    image['scale'] = float(imageScaleFactor) * float(image['array'].shape[0]) / float(arms['armLength'])
    image['width'] = image['array'].shape[0]/image['scale']
    image['height'] = image['array'].shape[1]/image['scale']
    image['currentXInArray'] = image['currentYInArray'] = False
    image['treshold'] = float(settingsTreshold.value)
    image['edgeAlgorithm'] = str(settingsAlgorithm.value)
    image['outputSize'] = int(settingsOutputSize.value)

def uploadBut():
    file_source.on_change('data', callbackFile)

    button = Button(label="Choose file..", width = 500)
    button.callback = CustomJS(args=dict(file_source=file_source), code = """
    function read_file(filename) {
        var reader = new FileReader();
        reader.onload = load_handler;
        reader.onerror = error_handler;
        // readAsDataURL represents the file's data as a base64 encoded string
        reader.readAsDataURL(filename);
    }

    function load_handler(event) {
        var b64string = event.target.result;
        file_source.data = {'file_contents' : [b64string], 'file_name':[input.files[0].name]};
        file_source.trigger("change");
    }

    function error_handler(evt) {
        if(evt.target.error.name == "NotReadableError") {
            alert("Can't read file!");
        }
    }

    var input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.onchange = function(){
        if (window.FileReader) {
            read_file(input.files[0]);
        } else {
            alert('FileReader is not supported in this browser');
        }
    }
    input.click();
    """)
    return button

def imageTab():
    imageTabElements = column(
                row(column(chooseFileLabel,chooseFileButton), settingsInputFilename),
                #row(settingsInputFilename, settingsOutputFilename),
                #settingsOutputSize,
                #row(settingsEdgeAlgorithm,settingsTreshold),
                #row(processImageButton,refreshButton),
                row(settingsOutputSize, settingsTreshold, settingsAlgorithm),
                row(changeResolutionButton, changeTresholdButton, changeAlgorithmButton),
                showImageResult,
                showImageOrig,
                showImageResize,
                showImageEdge,
                showImageInv)
    tabImage = Panel(child = imageTabElements, title = "Image processing", name = "imagetab")
    return tabImage

def calibrationTab():
    calibrationTabElements = column(
        row(calibrateInnerArmMinPulseSlider, calibrateInnerArmMaxPulseSlider),
        row(calibrateOuterArmMinPulseSlider, calibrateOuterArmMaxPulseSlider),
        row(calibratePenDownAngleSlider, calibratePenUpAngleSlider),
        row(calibrateInnerArmButton, calibrateOuterArmButton, calibratePenButton),
        row(calibrateUpdateButton, calibrateWriteConfigButton),
        calibrateInfo
    )
    tabCalibration = Panel(child = calibrationTabElements, title = 'Calibration', name = 'calibrationtab')
    return tabCalibration

def randomChar(y):
    return ''.join(choice(string.ascii_letters) for x in range(y))

# RasPi tab
def loggingTab():
    info = Div(text="""<img src="drawing-robot/static/out_orig.png">""")
    tabRaspi = Panel(child = info, title = "Logging informations")
    return tabRaspi

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
                setAngle(arms,raspi, 'far')
                movePen(arms, raspi, 'down')
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
                        setAngle(arms,raspi,'near')
                    findAdjacentPixel(image)
        print('finished drawing line ', image['lineCounter'])

    else:
        # hurray, we finished drawing
        print('Done drawing ', image['pixelCounter'], ' pixel in ', image['lineCounter'], 'lines.')
        # delete variables in dictionary:
        image['currentX'] = image['currentY'] = image['currentXInArray'] = image['currentYInArray'] = False
        image['currentLineX'] = image['currentLineY'] = []
        callbackStartButton() # stop autorefresh
        return

### what to be one once the browser window is updated:
def update():
    drawLine(image, arms, raspi)
    if raspi['switchedOn']:
        movePen(arms, raspi, 'up')

### populating image dictionary:
image['array'] = imageAsArray('out_result.png', image['treshold'])
image['scale'] = float(imageScaleFactor) * float(image['array'].shape[0]) / float(arms['armLength'])
image['width'] = image['array'].shape[0]/image['scale']
image['height'] = image['array'].shape[1]/image['scale']
image['currentXInArray'] = image['currentYInArray'] = False

### behaviour of start and reset button:
button = Button(label='Start', button_type='success')
button.on_click(callbackStartButton)
resetButton = Button(label='Reset', button_type='danger')
resetButton.on_click(callbackResetButton)


### UI elements
# UI elements for image tab:
settingsImageScale = TextInput(value=str(imageScaleFactor), title="Image scale:")
#settingsOutputFilename = TextInput(value=str(image['outputFilename']), title="Filename of output file:")
settingsInputFilename = TextInput(value=str(image['inputFilename']), title="Filename of input file:")
settingsTreshold = Slider(start=0, end=1, value=0.8, step=.01,
                      title="Threshold for conversion to black & white")
settingsOriginX = TextInput(value=str(image['originX']), title="Origin x:")
settingsOriginY = TextInput(value=str(image['originY']), title="Origin y:")
#settingsEdgeAlgorithm = MultiSelect(value=[str(image['edgeAlgorithm'])], title="Edgde detection algorithm:",
                                        # options=['scharr','frangi','canny'])
settingsOutputSize = Slider(start=50, end=500, step=10, value=image['outputSize'],
                            title="Resolution of output image")
settingsAlgorithm = Select(options = ['roberts', 'sobel', 'scharr', 'prewitt', 'canny-1', 'canny-2', 'canny-3'],
                           value=image['edgeAlgorithm'])
chooseFileLabel = Div(text="""""")
chooseFileButton = uploadBut()
changeTresholdButton = Button(label="Change Threshold", button_type="primary")
changeTresholdButton.on_click(callbackTreshold)
changeResolutionButton = Button(label="Change Resolution", button_type="primary")
changeResolutionButton.on_click(callbackSize)
changeAlgorithmButton = Button(label="Change Edge Algorithm", button_type="primary")
changeAlgorithmButton.on_click(callbackAlgorithm)

showImageOrig = bp.Figure(plot_width=int(simulation['sizeX']), plot_height=int(simulation['sizeY']), title="Original image", name="original")
showImageOrig.toolbar.logo = None
showImageOrig.toolbar_location = None
showImageOrig.toolbar.active_inspect = None
showImageOrig.toolbar.active_scroll = None
showImageOrig.toolbar.active_tap = None
showImageOrig.toolbar.active_drag = None
showImageOrig.x_range=Range1d(start=0, end=simulation['sizeX'])
showImageOrig.y_range=Range1d(start=0, end=simulation['sizeY'])
showImageOrig.xaxis.visible = None
showImageOrig.yaxis.visible = None
showImageOrig.xgrid.grid_line_color = None
showImageOrig.ygrid.grid_line_color = None

showImageResize = bp.Figure(plot_width=int(simulation['sizeX']), plot_height=int(simulation['sizeY']), title="Resized image")
showImageResize.toolbar.logo = None
showImageResize.toolbar_location = None
showImageResize.toolbar.active_inspect = None
showImageResize.toolbar.active_scroll = None
showImageResize.toolbar.active_tap = None
showImageResize.toolbar.active_drag = None
showImageResize.x_range=Range1d(start=0, end=simulation['sizeX'])
showImageResize.y_range=Range1d(start=0, end=simulation['sizeX'])
showImageResize.xaxis.visible = None
showImageResize.yaxis.visible = None
showImageResize.xgrid.grid_line_color = None
showImageResize.ygrid.grid_line_color = None

showImageInv = bp.Figure(plot_width=int(simulation['sizeX']), plot_height=int(simulation['sizeY']), title="Inverted image")
showImageInv.toolbar.logo = None
showImageInv.toolbar_location = None
showImageInv.toolbar.active_inspect = None
showImageInv.toolbar.active_scroll = None
showImageInv.toolbar.active_tap = None
showImageInv.toolbar.active_drag = None
showImageInv.x_range=Range1d(start=0, end=simulation['sizeX'])
showImageInv.y_range=Range1d(start=0, end=simulation['sizeX'])
showImageInv.xaxis.visible = None
showImageInv.yaxis.visible = None
showImageInv.xgrid.grid_line_color = None
showImageInv.ygrid.grid_line_color = None

showImageEdge = bp.Figure(plot_width=int(simulation['sizeX']), plot_height=int(simulation['sizeY']), title="Image after edge detection")
showImageEdge.toolbar.logo = None
showImageEdge.toolbar_location = None
showImageEdge.toolbar.active_inspect = None
showImageEdge.toolbar.active_scroll = None
showImageEdge.toolbar.active_tap = None
showImageEdge.toolbar.active_drag = None
showImageEdge.x_range=Range1d(start=0, end=simulation['sizeX'])
showImageEdge.y_range=Range1d(start=0, end=simulation['sizeX'])
showImageEdge.xaxis.visible = None
showImageEdge.yaxis.visible = None
showImageEdge.xgrid.grid_line_color = None
showImageEdge.ygrid.grid_line_color = None

showImageResult = bp.Figure(plot_width=int(simulation['sizeX']), plot_height=int(simulation['sizeY']),
                            title='Image that will be drawn', sizing_mode='scale_width')
showImageResult.toolbar.logo = None
showImageResult.toolbar_location = None
showImageResult.x_range=Range1d(start=0, end=simulation['sizeX'])
showImageResult.y_range=Range1d(start=0, end=simulation['sizeX'])
showImageResult.xaxis.visible = None
showImageResult.yaxis.visible = None
showImageResult.xgrid.grid_line_color = None
showImageResult.ygrid.grid_line_color = None

showImageDiv = Div(text="""<img src="drawing-robot/static/out_orig.png>""")


header = Div(text="""<h2>Settings</h2><h3>General</h3>""")
headerRobot = Div(text="""<h3>Robot</h3>""")
headerSimulator = Div(text="""<h3>Simulator</h3>""")

# include checkbox for on/off
# UI elements for robot settings:
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
# UI elements for saving / reading config:
settingsUpdate = Button(label='Update settings', width=200)
settingsUpdateConfig = Button(label='Update settings and write to config', width=200)
settingsReadConfig = Button(label='Read settings from config', width=200)
# UI elements for simulator settings:
#include checkbox for on/off
settingsBrowser = TextInput(value=str(simulation['browser']), title="Browser used:")
settingsPenWidth = TextInput(value=str(simulation['penWidth']), title="Width of pen:")
settingsPenColor = TextInput(value=str(simulation['penColor']), title="Color of pen:")
settingsSizeX = TextInput(value=str(simulation['sizeX']), title="Width of simulation window:")
settingsSizeY = TextInput(value=str(simulation['sizeY']), title="Height of simulation window:")
#include checkbox for animate arms

### calibration tab objects
calibrateUpdateButton = Button(label='Update values!', width=200, button_type='warning')
calibrateUpdateButton.on_click(callbackUpdateCalibration)
calibrateWriteConfigButton = Button(label='Write values to config file!', width=200, button_type='danger')
calibrateWriteConfigButton.on_click(callbackWriteConfig)
calibrateInnerArmButton = Button(label='Calibrate inner arm', width=200)
calibrateInnerArmButton.on_click(callbackCalibrateInnerArmButton)
calibrateOuterArmButton = Button(label='Calibrate outer arm', width=200)
calibrateOuterArmButton.on_click(callbackCalibrateOuterArmButton)
calibratePenButton = Button(label='Calibrate Pen position', width=200)
calibratePenButton.on_click(callbackCalibratePenButton)
calibrateInnerArmMinPulseSlider = Slider(start=500, end=1500, value=arms['innerArmMinPulse'] , step=10,
                      title="inner arm minimum pulse")
calibrateInnerArmMaxPulseSlider = Slider(start=2000, end=4000, value=arms['innerArmMaxPulse'] , step=10,
                      title="inner arm maximum pulse")
calibrateOuterArmMinPulseSlider = Slider(start=500, end=1500, value=arms['outerArmMinPulse'] , step=10,
                      title="outer arm minimum pulse")
calibrateOuterArmMaxPulseSlider = Slider(start=2000, end=4000, value=arms['outerArmMaxPulse'] , step=10,
                      title="outer arm maximum pulse")
calibratePenDownAngleSlider = Slider(start=0, end=180, value=arms['penDownAngle'] , step=10,
                      title="pen down angle")
calibratePenUpAngleSlider = Slider(start=0, end=180, value=arms['penUpAngle'] , step=10,
                      title="pen up angle")
calibrateInfo = PreText(text="""information will be displayed here..""",
width=600, height=100)



### setting up raspi:
if raspi['switchedOn']:
    setupRaspi(arms, raspi)

### setting up the browser window
tab1 = imageTab()
#tab2 = settingsTab()
tab3 = setupSimulation(simulation, image, arms)
#tab4 = loggingTab()
#tab5 = calibrationTab()
tabs = Tabs(tabs = [tab1, tab3], sizing_mode='scale_width')
#layout = column(children=[row(button, resetButton), tabs], sizing_mode='scale_width', name='mainLayout')
layout = column(children=[button, tabs], sizing_mode='scale_width', name='mainLayout')
curdoc().title = "Drawing Robot"
curdoc().add_root(layout)
