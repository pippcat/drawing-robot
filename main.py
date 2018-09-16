#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
drawing-robot

invoke with 'bokeh serve --show drawing-robot-headless' and open
in browser (localhost:5006)
"""

### libraries
# external
import base64
import logging
import os
import shutil
import string
import pandas as pd
import configparser # for importing config file
import bokeh.plotting as bp
import threading
from random import choice
from io import BytesIO
from time import sleep
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.events import ButtonClick
from bokeh.io import curdoc
from bokeh.models import Panel, Button, Range1d, Plot
from bokeh.models.widgets import Tabs, Div, TextInput, Select, Slider, PreText
from bokeh.layouts import column, row, WidgetBox

# own stuff:
from helper import get_angles
from helper import find_pixel
from helper import find_adjacent_pixel
from imageProcessor.imageProcessor import open_image
from imageProcessor.imageProcessor import detect_edges
from imageProcessor.imageProcessor import invert_images
from imageProcessor.imageProcessor import resize_image
from imageProcessor.imageProcessor import save_file
from imageProcessor.imageProcessor import image_as_array
from simulator.simulator import set_up_simulation
from simulator.simulator import update_simulation_background
from simulator.simulator import move_arms
from simulator.simulator import draw_new_line
from simulator.simulator import append_line
from simulator.simulator import draw_pixel
# from raspiRobot.raspiRobot import move_pen
# from raspiRobot.raspiRobot import set_up_raspi
# from raspiRobot.raspiRobot import set_angle
# from raspiRobot.raspiRobot import calibrate

# is needed for image import:
file_source = ColumnDataSource({'file_contents':[], 'file_name':[]})

# multithreading of simulator and robot:
threadList = []

### reading variables from config file:
config = configparser.ConfigParser()
config.read('drawing-robot/config.ini')
#config.read('config.ini')
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
arms = {'innerArmLength':innerArmLength,
        'innerArmAngleRad':0,
        'innerArmAngleDeg':0,
        'innerArmChannel':innerArmChannel,
        'innerArmActuationRange':innerArmActuationRange,
        'innerArmMinPulse':innerArmMinPulse,
        'innerArmMaxPulse':innerArmMaxPulse,
        'outerArmLength':outerArmLength,
        'outerArmAngleRad':0,
        'innerArmAngleDeg':0,
        'outerArmChannel':outerArmChannel,
        'outerArmActuationRange':outerArmActuationRange,
        'outerArmMinPulse':outerArmMinPulse,
        'outerArmMaxPulse':outerArmMaxPulse,
        'penUpAngle':penUpAngle,
        'penDownAngle':penDownAngle,
        'penChannel':penChannel,
        'armLength': innerArmLength + outerArmLength}

image = {'inputFilename':"",
         'outputFilename':outputFilename,
         'treshold':treshold,
         'originX':originX,
         'originY':originY,
         'edgeAlgorithm':edgeAlgorithm,
         'lineCounter':0,
         'pixelCounter':0,
         'currentLineX':[],
         'currentLineY':[],
         'skipProcessing':skipProcessing,
         'foundNextPixel':True,
         'foundLastPixel':False,
         'outputSize':outputSize}

raspi = {'switchedOn':raspiSwitchedOn,
         'frequency':frequency,
         'waitTimeNear':waitTimeNear,
         'waitTimeFar':waitTimeFar,
         'waitTimePen':waitTimePen,
         'calibrateOuterArm': 0,
         'calibrateInnerArm': 0,
         'calibratePen': 0}

simulation = {'switchedOn':simulatorSwitchedOn,
              'browser':browser,
              'sizeX':sizeX,
              'sizeY':sizeY,
              'penWidth':penWidth,
              'penColor':penColor,
              'animateArms':animateArms,
              'lines':[]}

# needed for periodic callbacks:
callback_id = None

### callback functions:
def callback_size():
    '''Changes size of output image.'''
    update_image_settings()
    name = get_random_char(2)
    im = open_image(image['inputFilename']) # open image
    save_file(name + '_orig.png', im)
    res = resize_image(im,image['outputSize']) # resize it
    save_file(name + '_scaledown.png', res)
    edge = detect_edges(res, image['edgeAlgorithm']) # detect edges
    save_file(name + '_edge.png', edge)
    inv = invert_images(edge) # invert result
    save_file(name + '_inv.png', inv) # save file
    result = image_as_array(name + '_inv.png', image['treshold'])
    image['array'] = result
    save_file(name + '_result.png', result)
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                            name + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                                 name + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                            name + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                           name + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                              name + '_result.png']))
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
    update_simulation_background(simulation, image)

def callback_treshold():
    '''Changes threshold value of 1-bit image array.'''
    update_image_settings()
    name = get_random_char(2)
    im = open_image(image['outputFilename'] + '_inv.png') # open image
    save_file(name + '_inv.png', im)
    result = image_as_array(image['outputFilename'] + '_inv.png',
                            image['treshold']) # store as array
    image['array'] = result
    #save_file(image['outputFilename'] + '_result.png', result)
    save_file(name + '_result.png', result)
    #img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' +
    #                        image['outputFilename'] + '_result.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                              name + '_result.png']))
    showImageResult.image_url(url='url', x=0, y=500,
        h=float(simulation['sizeX'])/float(result.shape[0])*
            float(result.shape[1]),
        w=simulation['sizeX'],
        source=img_result)
    image['outputFilename'] = name
    update_simulation_background(simulation, image)

def callback_calibrate_outer_arm():
    '''Drives outer arm to predefined positions.'''
    raspi['calibrateOuterArm'] += 1
    if raspi['calibrateOuterArm'] == 1:
        calibrate(arms, raspi, "outerArm", 45)
        calibrateInfo.text = """outerArm moved to 45deg,
        check if angle is right and press button again!"""
    if raspi['calibrateOuterArm'] == 2:
        calibrate(arms, raspi, "outerArm", 90)
        calibrateInfo.text = """outerArm moved to 90deg,
        check if angle is right and press button again!"""
    if raspi['calibrateOuterArm'] == 3:
        calibrate(arms, raspi, "outerArm", 180)
        calibrateInfo.text = """outerArm moved to 180deg,
        check if angle is right and press button again!"""
    if raspi['calibrateOuterArm'] == 4:
        raspi['calibrateOuterArm'] = 0
        calibrate(arms, raspi, "outerArm", 90)
        calibrateInfo.text = """outerArm moved to 90deg,
        calibration procedure done.
        Adjust outerArmMinPulse and outerArmMaxPulse
        and redo procedure until angles are good!"""

def callback_calibrate_inner_arm():
    '''Drives inner arm to predefined positions.'''
    raspi['calibrateInnerArm'] += 1
    if raspi['calibrateInnerArm'] == 1:
        calibrate(arms, raspi, "innerArm", 0)
        calibrateInfo.text = """innerArm moved to 0deg,
        check if angle is right and press button again!"""
    if raspi['calibrateInnerArm'] == 2:
        calibrate(arms, raspi, "innerArm", 90)
        calibrateInfo.text = """innerArm moved to 90deg,
        check if angle is right and press button again!"""
    if raspi['calibrateInnerArm'] == 3:
        calibrate(arms, raspi, "innerArm", 180)
        calibrateInfo.text = """innerArm moved to 180deg,
        check if angle is right and press button again!"""
    if raspi['calibrateInnerArm'] == 4:
        raspi['calibrateInnerArm'] = 0
        calibrate(arms, raspi, "innerArm", 90)
        calibrateInfo.text = """innerArm moved to 90deg,
        calibration procedure done.
        Adjust innerArmMinPulse and innerArmMaxPulse
        and redo procedure until angles are good!"""

def callback_calibrate_pen():
    '''Moves pen up an down to check angles.'''
    raspi['calibratePen'] += 1
    if raspi['calibratePen'] == 1:
        calibrate(arms, raspi, "pen", 110, "down")
        calibrateInfo.text = """pen moved down, check if angle is right!"""
    if raspi['calibratePen'] == 2:
        calibrate(arms, raspi, "pen", 110, "up")
        calibrateInfo.text = """pen moved up, check if angle is right!"""
    if raspi['calibratePen'] == 3:
        raspi['calibratePen'] = 0

def callback_update_calibration():
    '''Updates robot arm settings.'''
    arms['innerArmMinPulse'] = calibrateInnerArmMinPulseSlider.value
    arms['innerArmMaxPulse'] = calibrateInnerArmMaxPulseSlider.value
    arms['outerArmMinPulse'] = calibrateOuterArmMinPulseSlider.value
    arms['outerArmMaxPulse'] = calibrateOuterArmMaxPulseSlider.value
    arms['penDownAngle'] = calibratePenDownAngleSlider.value
    arms['penUpAngle'] = calibratePenUpAngleSlider.value
    calibrateInfo.text = """Calibration values updated!"""

def callback_write_config():
    '''Writes values from web interface back to config file.'''
    print('config will be written now!')

def callback_algorithm():
    '''Does edge calculation after changing the algorithm.'''
    update_image_settings()
    name = get_random_char(2)
    im = open_image(image['outputFilename'] + '_scaledown.png') # open image
    save_file(name + '_scaledown.png', im)
    edge = detect_edges(im, str(image['edgeAlgorithm'])) # detect edges
    save_file(name + '_edge.png', edge)
    inv = invert_images(edge) # invert result
    save_file(name + '_inv.png', inv) # save file
    result = image_as_array(name + '_inv.png', image['treshold'])
    image['array'] = result
    save_file(name + '_result.png', result)
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                            name + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                                 name + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                            name + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                           name + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                              name + '_result.png']))
    img_orig.data.update(dict(url = ['drawing-robot/static/' +
                                     name + '_orig.png']))
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
    update_simulation_background(simulation, image)


def callback_file_upload(attr,old,new):
    '''Handles file upload.'''
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
    update_image_settings()
    #save settings before!
    name = get_random_char(2)
    #name = image['inputFilename']
    logging.info('Image name on hard disk:' + str(name))
    im = open_image(image['inputFilename']) # open image
    save_file(name + '_orig.png', im)
    res = resize_image(im,image['outputSize']) # resize it
    save_file(name + '_scaledown.png', res)
    edge = detect_edges(res, str(image['edgeAlgorithm'])) # detect edges
    save_file(name + '_edge.png', edge)
    inv = invert_images(edge) # invert result
    save_file(name + '_inv.png', inv) # save file
    result = image_as_array(name + '_inv.png', image['treshold'])
    image['array'] = result
    save_file(name + '_result.png', result)
    img_orig = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                    name + '_orig.png']))
    img_scaledown = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                    name + '_scaledown.png']))
    img_edge = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                    name + '_edge.png']))
    img_inv = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                    name + '_inv.png']))
    img_result = ColumnDataSource(dict(url = ['drawing-robot/static/' +
                                    name + '_result.png']))
    img_orig.data.update(dict(url = ['drawing-robot/static/' +
                                    name + '_orig.png']))
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
    update_simulation_background(simulation, image)

def callback_start():
    '''Starts/stops the drawing process.'''
    global callback_id
    if button.label == 'Start':
        button.label = 'Stop'
        button.button_type = 'warning'
        callback_id = curdoc().add_periodic_callback(update, 200)
    else:
        button.label = 'Start'
        button.button_type = 'success'
        curdoc().remove_periodic_callback(callback_id)

def update_image_settings():
    '''Reads image settings from web interface and updates dictionary.'''
    image['scale'] = float(imageScaleFactor) * float(image['array'].shape[0]) / float(arms['armLength'])
    image['width'] = image['array'].shape[0]/image['scale']
    image['height'] = image['array'].shape[1]/image['scale']
    image['currentXInArray'] = image['currentYInArray'] = False
    image['treshold'] = float(settingsTreshold.value)
    image['edgeAlgorithm'] = str(settingsAlgorithm.value)
    image['outputSize'] = int(settingsOutputSize.value)

def upload_button():
    '''Handles file selection via JavaScript.'''
    file_source.on_change('data', callback_file_upload)
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
        file_source.data = {'file_contents' : [b64string],
            'file_name':[input.files[0].name]};
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

### parts of browser window:
def tab_settings():
    '''Defines the settings tab in the web interface.'''
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

def tab_image():
    '''Defines the image tab in the web interface.'''
    imageTabElements = column(
                row(column(chooseFileLabel,chooseFileButton),
                    settingsInputFilename),
                #row(settingsInputFilename, settingsOutputFilename),
                #settingsOutputSize,
                #row(settingsEdgeAlgorithm,settingsTreshold),
                #row(processImageButton,refreshButton),
                row(settingsOutputSize, settingsTreshold, settingsAlgorithm),
                row(changeResolutionButton, changeTresholdButton,
                    changeAlgorithmButton),
                showImageResult,
                showImageOrig,
                showImageResize,
                showImageEdge,
                showImageInv)
    tabImage = Panel(child = imageTabElements, title = "Image processing",
                                               name = "imagetab")
    return tabImage

def tab_calibration():
    '''Defines the calibration tab in the web interface.'''
    calibrationTabElements = column(
        row(calibrateInnerArmMinPulseSlider, calibrateInnerArmMaxPulseSlider),
        row(calibrateOuterArmMinPulseSlider, calibrateOuterArmMaxPulseSlider),
        row(calibratePenDownAngleSlider, calibratePenUpAngleSlider),
        row(calibrateInnerArmButton, calibrateOuterArmButton,
            calibratePenButton),
        row(calibrateUpdateButton, calibrateWriteConfigButton),
        calibrateInfo
    )
    tabCalibration = Panel(child = calibrationTabElements,
                           title = 'Calibration', name = 'calibrationtab')
    return tabCalibration

def tab_logging():
    '''Defines the logging tab in the web interface.'''
    info = Div(text="""<img src="drawing-robot/static/out_orig.png">""")
    tabRaspi = Panel(child = info, title = "Logging informations")
    return tabRaspi

def get_random_char(y):
    '''Gives back a number of random chars.'''
    return ''.join(choice(string.ascii_letters) for x in range(y))

def draw_line(image, arms, raspi):
    '''This is the main drawing function which is draws the image in the
    simulator and in the real world.'''
    # looking for the first pixel in image, sets image['foundNextPixel']:
    find_pixel(image)
    threadList=[] # delete the old thread list
    if image['foundNextPixel']:
        image['lineCounter'] += 1 # linecounter +1
        get_angles(image, arms) # calculate angles of robot arms
        if arms['innerArmAngleDeg'] != 0 and arms['outerArmAngleDeg'] != 0:
            if simulation['switchedOn']:
                draw_new_line(simulation, image)
                if simulation['animateArms']:
                    moveArmsThread = threading.Thread(move_arms(arms, simulation))
                    threadList.append(moveArmsThread)
                    #move_arms(arms, simulation)
            if raspi['switchedOn']:
                moveRobotThread = threading.Thread(move_then_down(arms, raspi))
                threadList.append(moveRobotThread)
                #move_then_down(arms,raspi)
            for thread in threadList:
                thread.start()
            for thread in threadList:
                thread.join()
            find_adjacent_pixel(image)
            if (not image['foundNextPixel']) and simulation['switchedOn']:
                draw_pixel(simulation, image)
            while image['foundNextPixel']:
                threadList=[] # delete the old thread list
                get_angles(image, arms)
                if arms['innerArmAngleDeg'] != 0 and arms['outerArmAngleDeg'] != 0:
                    if simulation['switchedOn']:
                        image['currentLineX'].append(image['currentX'])
                        image['currentLineY'].append(image['currentY'])
                        if simulation['animateArms']:
                            moveArmsThread = threading.Thread(move_arms(arms, simulation))
                            threadList.append(moveArmsThread)
                            #move_arms(arms, simulation)
                        appendLineThread = threading.Thread(append_line(simulation, image))
                        threadList.append(appendLineThread)
                        #append_line(simulation, image)
                    if raspi['switchedOn']:
                        moveRobotThread = threading.Thread(move_then_down(arms, raspi))
                        threadList.append(moveRobotThread)
                        #set_angle(arms,raspi,'near')
                    find_adjacent_pixel(image)
                for thread in threadList:
                    thread.start()
                for thread in threadList:
                    thread.join()
        logging.info('finished drawing line ' + str(image['lineCounter']))

    else:
        # hurray, we finished drawing
        logging.info('Done drawing ' + str(image['pixelCounter']) +
                ' pixel in ' + str(image['lineCounter']) + ' lines.')
        # delete variables in dictionary:
        image['currentX'] = image['currentY'] = False
        image['currentXInArray'] = image['currentYInArray'] = False
        image['currentLineX'] = image['currentLineY'] = []
        callback_start() # stop autorefresh
        return

### what to be one once the browser window is updated:
def update():
    '''Function is invoked by periodic callback.'''
    draw_line(image, arms, raspi)
    if raspi['switchedOn']:
        move_pen(arms, raspi, 'up')

### populating image dictionary:
image['array'] = image_as_array('out_result.png', image['treshold'])
image['scale'] = float(imageScaleFactor) * float(image['array'].shape[0]) / float(arms['armLength'])
image['width'] = image['array'].shape[0]/image['scale']
image['height'] = image['array'].shape[1]/image['scale']
image['currentXInArray'] = image['currentYInArray'] = False

### behaviour of start and reset button:
button = Button(label='Start', button_type='success')
button.on_click(callback_start)


### UI elements
# UI elements for image tab:
settingsImageScale = TextInput(value=str(imageScaleFactor),
                               title="Image scale:")
settingsInputFilename = TextInput(value=str(image['inputFilename']),
                                  title="Filename of input file:")
settingsTreshold = Slider(start=0, end=1, value=0.8, step=.01,
                      title="Threshold for conversion to black & white")
settingsOriginX = TextInput(value=str(image['originX']), title="Origin x:")
settingsOriginY = TextInput(value=str(image['originY']), title="Origin y:")

settingsOutputSize = Slider(start=50, end=500, step=10,
                            value=image['outputSize'],
                            title="Resolution of output image")
settingsAlgorithm = Select(options = ['roberts', 'sobel', 'scharr', 'prewitt',
                                      'canny-1', 'canny-2', 'canny-3'],
                           value=image['edgeAlgorithm'])
chooseFileLabel = Div(text="""""")
chooseFileButton = upload_button()
changeTresholdButton = Button(label="Change Threshold", button_type="primary")
changeTresholdButton.on_click(callback_treshold)
changeResolutionButton = Button(label="Change Resolution",
                                button_type="primary")
changeResolutionButton.on_click(callback_size)
changeAlgorithmButton = Button(label="Change Edge Algorithm",
                               button_type="primary")
changeAlgorithmButton.on_click(callback_algorithm)

showImageOrig = bp.Figure(plot_width=int(simulation['sizeX']),
                          plot_height=int(simulation['sizeY']),
                          title="Original image", name="original")
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

showImageResize = bp.Figure(plot_width=int(simulation['sizeX']),
                            plot_height=int(simulation['sizeY']),
                            title="Resized image")
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

showImageInv = bp.Figure(plot_width=int(simulation['sizeX']),
                         plot_height=int(simulation['sizeY']),
                         title="Inverted image")
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

showImageEdge = bp.Figure(plot_width=int(simulation['sizeX']),
                          plot_height=int(simulation['sizeY']),
                          title="Image after edge detection")
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

showImageResult = bp.Figure(plot_width=int(simulation['sizeX']),
                            plot_height=int(simulation['sizeY']),
                            title='Image that will be drawn',
                            sizing_mode='scale_width')
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
settingsInnerArmLength = TextInput(value=str(arms['innerArmLength']),
                                    title="Inner arm length:")
settingsInnerArmMinPulse= TextInput(value=str(arms['innerArmMinPulse']),
                                    title="Inner arm mininum pulse:")
settingsInnerArmMaxPulse= TextInput(value=str(arms['innerArmMaxPulse']),
                                    title="Inner arm maximum pulse:")
settingsInnerArmActuationRange= TextInput(
                                    value=str(arms['innerArmActuationRange']),
                                    title="Inner arm actuation range:")
settingsOuterArmLength = TextInput(value=str(arms['outerArmLength']),
                                    title="Outer arm length:")
settingsOuterArmMinPulse= TextInput(value=str(arms['outerArmMinPulse']),
                                    title="Outer arm mininum pulse:")
settingsOuterArmMaxPulse= TextInput(value=str(arms['outerArmMaxPulse']),
                                    title="Outer arm maximum pulse:")
settingsOuterArmActuationRange= TextInput(
                                    value=str(arms['outerArmActuationRange']),
                                    title="Outer arm actuation range:")
settingsPenUpAngle= TextInput(value=str(arms['penUpAngle']),
                                    title="Angle for pen up:")
settingsPenDownAngle= TextInput(value=str(arms['penDownAngle']),
                                    title="Angle for pen down:")
settingsWaitTimeNear= TextInput(value=str(raspi['waitTimeNear']),
                                    title="Wait time if next pixel is near:")
settingsWaitTimeFar= TextInput(value=str(raspi['waitTimeFar']),
                                    title="Wait time if next pixel is far:")
settingsWaitTimePen= TextInput(value=str(raspi['waitTimePen']),
                                    title="Wait time after pen movement:")
# UI elements for saving / reading config:
settingsUpdate = Button(label='Update settings', width=200)
settingsUpdateConfig = Button(label='Update settings and write to config',
                                    width=200)
settingsReadConfig = Button(label='Read settings from config', width=200)
# UI elements for simulator settings:
#include checkbox for on/off
settingsBrowser = TextInput(value=str(simulation['browser']),
                                    title="Browser used:")
settingsPenWidth = TextInput(value=str(simulation['penWidth']),
                                    title="Width of pen:")
settingsPenColor = TextInput(value=str(simulation['penColor']),
                                    title="Color of pen:")
settingsSizeX = TextInput(value=str(simulation['sizeX']),
                                    title="Width of simulation window:")
settingsSizeY = TextInput(value=str(simulation['sizeY']),
                                    title="Height of simulation window:")
#include checkbox for animate arms

### calibration tab objects
calibrateUpdateButton = Button(label='Update values!', width=200,
                               button_type='warning')
calibrateUpdateButton.on_click(callback_update_calibration)
calibrateWriteConfigButton = Button(label='Write values to config file!',
                                    width=200, button_type='danger')
calibrateWriteConfigButton.on_click(callback_write_config)
calibrateInnerArmButton = Button(label='Calibrate inner arm', width=200)
calibrateInnerArmButton.on_click(callback_calibrate_inner_arm)
calibrateOuterArmButton = Button(label='Calibrate outer arm', width=200)
calibrateOuterArmButton.on_click(callback_calibrate_outer_arm)
calibratePenButton = Button(label='Calibrate Pen position', width=200)
calibratePenButton.on_click(callback_calibrate_pen)
calibrateInnerArmMinPulseSlider = Slider(start=500, end=1500,
                                         value=arms['innerArmMinPulse'],
                                         step=10,
                                         title="inner arm minimum pulse")
calibrateInnerArmMaxPulseSlider = Slider(start=2000, end=4000,
                                         value=arms['innerArmMaxPulse'],
                                         step=10,
                                         title="inner arm maximum pulse")
calibrateOuterArmMinPulseSlider = Slider(start=500, end=1500,
                                         value=arms['outerArmMinPulse'],
                                         step=10,
                                         title="outer arm minimum pulse")
calibrateOuterArmMaxPulseSlider = Slider(start=2000, end=4000,
                                         value=arms['outerArmMaxPulse'] ,
                                         step=10,
                                         title="outer arm maximum pulse")
calibratePenDownAngleSlider = Slider(start=0, end=180,
                                         value=arms['penDownAngle'],
                                         step=10,
                                         title="pen down angle")
calibratePenUpAngleSlider = Slider(start=0, end=180,
                                         value=arms['penUpAngle'],
                                         step=10,
                                         title="pen up angle")
calibrateInfo = PreText(text="""information will be displayed here..""",
width=600, height=100)



### setting up raspi:
if raspi['switchedOn']:
    set_up_raspi(arms, raspi)

### setting up the browser window
tab1 = tab_image()
#tab2 = tab_settings()
tab3 = set_up_simulation(simulation, image, arms)
#tab4 = tab_logging()
#tab5 = tab_calibration()
tabs = Tabs(tabs = [tab1, tab3], sizing_mode='scale_width')
layout = column(children=[button, tabs], sizing_mode='scale_width',
                name='mainLayout')
curdoc().title = "Drawing Robot"
curdoc().add_root(layout)
