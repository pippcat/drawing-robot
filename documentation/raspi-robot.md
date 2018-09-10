Raspi-Robot
==========

Software needed
---------------

I used [Raspbian](https://www.raspberrypi.org/downloads/raspbian/). You have to install some additional software:

`sudo apt install python3-rpi.gpio git`

Then clone the repo:

`git clone https://github.com/pippcat/drawing-robot.git`

Change the cwd:

`cd drawing-robot/raspi-robot`

And execute the program:

`python3 raspi-robot.py`

Specs of the motors
-------------------

* MG90S:
** Weight: 13.4 g 
** Dimension: 22.5 x 12 x 35.5
** Stall torque: 1.8 kgf/cm (4.8V )
** Operating speed: 0.1 s/60 degree
** Operating voltage: 4.8 V - 6.0V
** Dead band width: 5 μs
** PWM period: 50 Hz / 20ms
** duty cycle: 1-2ms (1ms = -90°; 1,5ms = 0°; 2ms = 90°)

* LDX218:
** Weight: 60g
** Dimension: 40*20*40.5mm
** Speed: 0.16sec/60°(7.4V)
** Accuracy: 0.3°
** Torque: 15 kg/cm @6.6V; 17 kg/cm @7.4V
** Working Voltage: 6-7.4V
** MIn Working Current: 1A
** No-Load Current: 100mA
** Spline: 25T(6mm diameter)
** Control Method: PWM
** Pulse Width: 500~2500
** Duty Ratio: 0.5ms~2.5ms
** Pulse Period: 20ms

 
