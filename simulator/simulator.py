#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# a drawing robot simulator, runs in your browser

import bokeh.plotting as bp
import numpy as np
import logging
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
    # check if we have an old figure to delete before;



    logging.info('Intitializing drawing simulator')
    imageFrameX = ([image['originX'],
                    image['originX']+image['width'],
                    image['originX']+image['width'],
                    image['originX'],
                    image['originX']])
    imageFrameY = ([image['originY'],
                    image['originY'],
                    image['originY']+image['height'],
                    image['originY']+image['height'],
                    image['originY']])
    iads = ColumnDataSource(dict(x=[0], y=[0], l=[arms['innerArmLength']],
                        a=[0], n=["innerArm"], c=["midnightblue"], w=["6"]))
    oads = ColumnDataSource(dict(x=[arms['innerArmLength']], y=[0],
                        l=[arms['outerArmLength']], a=[0], n=["outerArm"],
                        c=["dodgerblue"], w=["6"]))
    sim = bp.figure(width=simulation['sizeX'], height=simulation['sizeY'],
                    x_range=(-0.25*arms['armLength'],arms['armLength']),
                    y_range=(0,1.25*arms['armLength']), name='simulatorPlot')
    # add a line for inner arm without data:
    innerArm = Ray(x="x", y="y", angle="a", length="l", name="n",
                   line_width="w", line_color="c")
    # add a line for outer arm without data
    outerArm = Ray(x="x", y="y", angle="a", length="l", name="n",
                   line_width="w", line_color="c")
    sim.add_glyph(iads, innerArm)
    sim.add_glyph(oads, innerArm)
    sim.circle(0,0,line_color="deeppink",line_width=3,radius=arms['armLength'],
               fill_color="deeppink",fill_alpha=0.1)
    sim.line(imageFrameX, imageFrameY, line_width=3, color="deeppink")
    simulation['backgroundImageDF'] = ColumnDataSource(dict(url = []))
    tab = Panel(child = sim, title = "Simulator")
    simulation['innerArmDataStream'] = iads
    simulation['outerArmDataStream'] = oads
    simulation['figure'] = sim
    return tab

def update_simulation_background(simulation, image):
    '''Updates the simulation background image after modifying it.
    it also removes the already drawn lines of the old images.'''
    logging.info('Updating drawing simulator backgound image.')
    #remove old lines; how to do that better?:
    if image['lineCounter'] > 0:
        for a in simulation['lines']:
            ds = a.data.copy()
            ds['x'] = []
            ds['y'] = []
            a.data = ds

    simulation['lines'] =  [ColumnDataSource(dict(x=[], y=[]))]
    simulation['backgroundImageDF'].data.update(dict(url =
        ['drawing-robot/static/' + image['outputFilename'] + '_result.png']))
    simulation['backgroundImage'] = simulation['figure'].image_url(url='url',
                    x=image['originX']-0.5,
                    y = image['height'] + image['originY']-0.5,
                    h=image['height'], w=image['width'],
                    global_alpha=0.3, source=simulation['backgroundImageDF'])
    # on debian with other version of bokeh this had to be:
    # y = image['height']/image['width']*image['height'] + image['originY']-0.5
    # h=image['height']/image['width']*image['height']

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
    '''we have to initialize 2 points to still draw anthing if
    there is no adjacent pixel:'''
    ds = ColumnDataSource(dict(x=[image['currentX']+0.25,image['currentX']-0.25],
                               y=[image['currentY'], image['currentY']]))
    newLine = Line(x="x", y="y", line_width=simulation['penWidth'],
                   line_color=simulation['penColor'],
                   name='line' + str(image['lineCounter']))
    simulation['lines'].append(ds)
    simulation['figure'].add_glyph(ds, newLine)

def append_line(simulation, image):
    '''Appends pixel to the current line in the simulator.'''
    newDS = simulation['lines'][-1].data
    newDS['x'].append(image['currentX'])
    newDS['y'].append(image['currentY'])
    simulation['lines'][-1].data = newDS
