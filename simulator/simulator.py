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

def set_up_simulation(simulation, image, arms):
    '''Sets up the simulation screen.'''
    iads = ColumnDataSource(dict(x=[0], y=[0], l=[arms['innerArmLength']], a=[0], n=["innerArm"], c=["midnightblue"], w=["6"]))
    oads = ColumnDataSource(dict(x=[arms['innerArmLength']], y=[0], l=[arms['outerArmLength']],
                                 a=[0], n=["outerArm"], c=["dodgerblue"], w=["6"]))
    sim = bp.figure(width=simulation['sizeX'], height=simulation['sizeY'],
                    x_range=(-0.25*arms['armLength'],arms['armLength']),
                    y_range=(0,1.25*arms['armLength']),
                    tools="")
    innerArm = Ray(x="x", y="y", angle="a", length="l", name="n", line_width="w", line_color="c") # add a line for inner arm without data
    outerArm = Ray(x="x", y="y", angle="a", length="l", name="n", line_width="w", line_color="c") # add a line for outer arm without data
    sim.add_glyph(iads, innerArm)
    sim.add_glyph(oads, innerArm)
    imageFrameX = [image['originX'],image['originX']+image['width'],image['originX']+image['width'],image['originX'],image['originX']]
    imageFrameY = [image['originY'],image['originY'],image['originY']+image['height'],image['originY']+image['height'],image['originY']]
    sim.line(imageFrameX, imageFrameY, line_width=3, color="deeppink")
    sim.circle(0,0,line_color="deeppink",line_width=3,radius=arms['armLength'],fill_color="deeppink",fill_alpha=0.1)
    simulation['backgroundImageDF'] = ColumnDataSource(dict(url = []))
    simulation['backgroundImage'] = sim.image_url(url='url', x=image['originX']-0.5,
        y = image['height'] + image['originY']-0.5,
        h=image['height'], w=image['width'],
        global_alpha=0.3, source=simulation['backgroundImageDF'])
    # on debian with other version of bokeh this had to be:
    # y = image['height']/image['width']*image['height'] + image['originY']-0.5
    # h=image['height']/image['width']*image['height']
    tab = Panel(child = sim, title = "Drawing robot")
    simulation['innerArmDataStream'] = iads
    simulation['outerArmDataStream'] = oads
    simulation['figure'] = sim
    return tab

def update_simulation_background(simulation, image):
    '''Updates the simulation background image after modifying it.'''
    simulation['backgroundImageDF'].data.update(dict(url = ['drawing-robot/static/' + image['outputFilename']
                                                                                     + '_result.png']))

def move_arms(arms, simulation):
    '''Moves the robot arms in the simulation during the drawing process.'''
    newInner = simulation['innerArmDataStream'].data
    newOuter = simulation['outerArmDataStream'].data
    newInner['a'] = [arms['innerArmAngleRad']]
    newOuter['a'] = [arms['innerArmAngleRad']-np.pi+arms['outerArmAngleRad']]
    newOuter['x'] = [arms['innerArmLength']*np.cos(arms['innerArmAngleRad'])]
    newOuter['y'] = [arms['innerArmLength']*np.sin(arms['innerArmAngleRad'])]
    simulation['innerArmDataStream'].data = newInner
    simulation['outerArmDataStream'].data = newOuter

def draw_new_line(simulation, image):
    '''Draws a new line in the simulator.'''
    ds = ColumnDataSource(dict(x=[image['currentX']], y=[image['currentY']]))
    newLine = Line(x="x", y="y", line_width=simulation['penWidth'], line_color=simulation['penColor'])
    simulation['lines'].append(ds)
    simulation['figure'].add_glyph(ds, newLine)

def append_line(simulation, image):
    '''Appends pixel to the current line in the simulator.'''
    newDS = simulation['lines'][-1].data
    newDS['x'].append(image['currentX'])
    newDS['y'].append(image['currentY'])
    simulation['lines'][-1].data = newDS

def draw_pixel(simulation, image):
    '''Draws a single pixel in the simulator if there is no line.'''
    simulation['figure'].rect(x=[image['currentX']], y=[image['currentY']],
        width=.5, height=.5, line_width=0.25*simulation['penWidth'], color=simulation['penColor'])
