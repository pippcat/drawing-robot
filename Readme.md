# Drawing robot


This project uses an RaspberryPi 3, a PCA9685,  some servo motors and a pen to draw a picture like a human would do.

The project uses [Bokeh](https://bokeh.pydata.org/en/latest/) and allows to upload and modify images in the webbrowser as well as simultaneously watch the drawing process in a simulator. Image upload from the controlling device is possible.

## Usage

### Startup

- check and modify [config.ini](config.ini)
- start with `bokeh serve drawing-robot` on level above the "drawing-robot" directory
- if you're using an external device to control it make sure that the IP is whitelisted: `bokeh serve --allow-websocket-origin localhost:5006 --allow-websocket-origin IP_OF_EXTERNAL_DEVICE:5006`

### Web Interface

- open the bokeh app in your browser: `http://localhost:5006/drawing-robot`
- upload an image by clicking on the `choose file` button
- check the image modification process by scrolling down
- you might want to change output size, threshold or edge detection algorithm and recalculate the result by clicking on `apply changes`
- if you're satisfied you might want to open the `simulator` Tab and start the drawing process by clicking onto the `start` button
- you can pause the drawing process by clicking on the `Stop` button - the robot will finish it's current line and halt then
- you might also go back to the `Image processing` tab and change the image, the drawing process and simulator will then be reset.

## Documentation

- See [documentation/installation-raspbian.md](documentation/installation-raspbian.md) for infos how to set things up on a RaspberryPi (3) using a fresh Raspbian.
- See [documentation/links.md](documentation/links.md) for some links related to the project.
- See [documentation/raspi-robot.md](documentation/raspi-robot.md) for more informations on setting up the Raspberry Pi.
