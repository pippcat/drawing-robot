#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# a drawing robot simulator, runs in your browser

import bokeh.plotting as bp
import numpy as np
import math
from random import random
from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.models import Panel, Button, ColumnDataSource, Plot
from bokeh.models.widgets import Tabs
from bokeh.models.glyphs import Ray
from bokeh.layouts import column
#import matplotlib.pyplot as pyplot

def setupSimulation(simulator, image, arms):
    iads = ColumnDataSource(dict(x=[0], y=[0], l=[arms['innerArmLength']], a=[0], n=["innerArm"], c=["midnightblue"], w=["6"]))
    oads = ColumnDataSource(dict(x=[arms['innerArmLength']], y=[0], l=[arms['outerArmLength']],
                                 a=[0], n=["outerArm"], c=["dodgerblue"], w=["6"]))
    #sim = bp.figure(title="Drawing Robot Simulator", width=sizeX, height=sizeY)
    sim = bp.figure(width=simulator['sizeX'], height=simulator['sizeY'],
                    x_range=(0,arms['armLength']),
                    y_range=(0,arms['armLength']))
    innerArm = Ray(x="x", y="y", angle="a", length="l", name="n", line_width="w", line_color="c") # add a line for inner arm without data
    outerArm = Ray(x="x", y="y", angle="a", length="l", name="n", line_width="w", line_color="c") # add a line for outer arm without data
    sim.add_glyph(iads, innerArm)
    sim.add_glyph(oads, innerArm)
    imageFrameX = [image['originX'],image['originX']+image['width'],image['originX']+image['width'],image['originX'],image['originX']]
    imageFrameY = [image['originY'],image['originY'],image['originY']+image['height'],image['originY']+image['height'],image['originY']]
    sim.line(imageFrameX, imageFrameY, line_width=3, color="deeppink")
    sim.circle(0,0,line_color="deeppink",line_width=3,radius=arms['armLength'],fill_color="deeppink",fill_alpha=0.1)
    sim.image(image=[image['array']], x=[image['originX']], y=[image['originY']],
              dw=[image['array'].shape[0]/image['scale']], dh=[image['array'].shape[1]/image['scale']], global_alpha=0.3)
    #innerArm = sim.line([originX, originOuterX], [originY, originOuterY], name = "innerArm", line_width = 2, color="navy")
    #sim.line([originOuterX, endX], [originOuterY, endY], name = "outerArm", line_width = 2, color="red")
    #button = Button(label="Press me")
    #tab = Panel(child = column(button,sim), title = "Simulator")
    tab = Panel(child = sim, title = "Simulator")
    return tab



def callback(iads):
    # BEST PRACTICE --- update .data in one step with a new dict
    newPos = dict()
    newPos['x'] = [random()*70]
    newPos['y'] = [random()*70]
    #newPos['line_width'] = iads.data['line_width']
    #newPos['color'] = iads.data['color']
    iads.data = newPos
