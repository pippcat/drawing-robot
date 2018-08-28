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

def setupSimulation(browser, sizeX, sizeY, innerArmLength, outerArmLength, originX, originY, imageScale):
    originOuterX = originOuterY = 60
    endX = endY = 15
    iads = ColumnDataSource(dict(x=[originX], y=[originY], l=[innerArmLength], a=[math.radians(90)]))
    #sim = bp.figure(title="Drawing Robot Simulator", width=sizeX, height=sizeY)
    sim = bp.figure(title="Drawing Robot Simulator", width=sizeX, height=sizeY)
    innerArm = Ray(x="x", y="y", angle="a", length="l", line_width=3, line_color="navy") # add a line for inner arm without data

    sim.add_glyph(iads, innerArm)
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
