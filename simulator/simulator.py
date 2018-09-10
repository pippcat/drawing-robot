#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# a drawing robot simulator, runs in your browser

import bokeh.plotting as bp
import numpy as np
from random import random
from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.models import Panel, Button, ColumnDataSource, Plot
from bokeh.models.widgets import Tabs
from bokeh.models.glyphs import Ray, Line, ImageURL
from bokeh.layouts import column
from time import sleep

def setupSimulation(simulation, image, arms):
    iads = ColumnDataSource(dict(x=[0], y=[0], l=[arms['innerArmLength']], a=[0], n=["innerArm"], c=["midnightblue"], w=["6"]))
    oads = ColumnDataSource(dict(x=[arms['innerArmLength']], y=[0], l=[arms['outerArmLength']],
                                 a=[0], n=["outerArm"], c=["dodgerblue"], w=["6"]))
    #sim = bp.figure(title="Drawing Robot Simulator", width=sizeX, height=sizeY)
    sim = bp.figure(width=simulation['sizeX'], height=simulation['sizeY'],
                    x_range=(-0.25*arms['armLength'],arms['armLength']),
                    y_range=(0,1.25*arms['armLength']))
    innerArm = Ray(x="x", y="y", angle="a", length="l", name="n", line_width="w", line_color="c") # add a line for inner arm without data
    outerArm = Ray(x="x", y="y", angle="a", length="l", name="n", line_width="w", line_color="c") # add a line for outer arm without data
    sim.add_glyph(iads, innerArm)
    sim.add_glyph(oads, innerArm)
    imageFrameX = [image['originX'],image['originX']+image['width'],image['originX']+image['width'],image['originX'],image['originX']]
    imageFrameY = [image['originY'],image['originY'],image['originY']+image['height'],image['originY']+image['height'],image['originY']]
    sim.line(imageFrameX, imageFrameY, line_width=3, color="deeppink")
    sim.circle(0,0,line_color="deeppink",line_width=3,radius=arms['armLength'],fill_color="deeppink",fill_alpha=0.1)
    #simulation['backgroundImage'] = ColumnDataSource(dict(url = ['drawing-robot/static/' + image['inputFilename'] + '_result.png']))
    #simulation['backgroundImage'] = ColumnDataSource(dict(url = []))
    simulation['backgroundImageDS'] = ColumnDataSource(dict(url = []))
    # simulation['figure'].image(image=[np.rot90(np.fliplr(image['array']))], x=image['originX']-0.5, y=image['originY']-0.5,
    #           dw=image['width'], dh=image['height'], global_alpha=0.3, name="backgroundImage")
    # sim.image_url(url='url', x=image['originX']-0.5, y = image['originY']-0.5,
    #             global_alpha=0.3, h=image['height'], w=image['width'], source=simulation['backgroundImage'])
    simulation['backgroundImage'] = ImageURL(url='url', x=image['originX']-0.5, y = image['originY']-0.5,
                global_alpha=0.3, h=image['height'], w=image['width'],  anchor="bottom_left")
    tab = Panel(child = sim, title = "Simulator")
    simulation['innerArmDataStream'] = iads
    simulation['outerArmDataStream'] = oads
    simulation['figure'] = sim
    simulation['glyph'] = simulation['figure'].add_glyph(simulation['backgroundImageDS'], simulation['backgroundImage'])
    return tab

def deleteOldBackground(simulation, image):
    print(image['outputFilename'])
    simulation['glyph'].visible = False

def updateSimulationBackground(simulation, image):
    print(image['outputFilename'])

    simulation['backgroundImageDS'] = ColumnDataSource(dict(url = ['drawing-robot/static/' + image['outputFilename']
                                                                                     + '_result.png']))
    simulation['glyph'] = simulation['figure'].add_glyph(simulation['backgroundImageDS'], simulation['backgroundImage'])
    # simulation['backgroundImage'] = ColumnDataSource(dict(url = ['drawing-robot/static/' + image['outputFilename']
    #                                                                                  + '_result.png']))
    # simulation['figure'].image_url(url='url', x=image['originX']-0.5, y = image['originY']+image['height']-0.5,
    #             global_alpha=0.3, h=image['height'], w=image['width'], source=simulation['backgroundImage   '])
def moveArms(arms, simulation):
    newInner = simulation['innerArmDataStream'].data
    newOuter = simulation['outerArmDataStream'].data
    newInner['a'] = [arms['innerArmAngleRad']]
    newOuter['a'] = [arms['innerArmAngleRad']-np.pi+arms['outerArmAngleRad']]
    newOuter['x'] = [arms['innerArmLength']*np.cos(arms['innerArmAngleRad'])]
    newOuter['y'] = [arms['innerArmLength']*np.sin(arms['innerArmAngleRad'])]
    simulation['innerArmDataStream'].data = newInner
    simulation['outerArmDataStream'].data = newOuter

def newLine(simulation, image):
    ds = ColumnDataSource(dict(x=[image['currentX']], y=[image['currentY']]))
    newLine = Line(x="x", y="y", line_width=simulation['penWidth'], line_color=simulation['penColor'])
    simulation['lines'].append(ds)
    simulation['figure'].add_glyph(ds, newLine)

def appendLine(simulation, image):
    newDS = simulation['lines'][-1].data
    newDS['x'].append(image['currentX'])
    newDS['y'].append(image['currentY'])
    simulation['lines'][-1].data = newDS

def drawPixel(simulation, image):
    simulation['figure'].rect(x=[image['currentX']], y=[image['currentY']],
        width=.5, height=.5, line_width=0.25*simulation['penWidth'], color=simulation['penColor'])
