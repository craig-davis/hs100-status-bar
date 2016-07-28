HS100 Status Bar App
===============================================================================
> A simple status bar app for controlling an HS100 Smart Plug

I have a very noise air conditioning unit in my office that I have to turn off
during conference calls. This is a small menu bar app that can control an HS100
smart plug. The air conditioner is plugged into the device, and I can now turn it on and off
with a click. Here is an ([affiliate link to Amazon for the device](http://amzn.to/2ajDxuN)).

The app is built with [Rumps](https://github.com/jaredks/rumps). It's a great
library for putting together status bar apps for OSX. It's really quite easy to
setup simple applications. Be sure to check [the examples](https://github.com/jaredks/rumps/tree/master/examples), there's quite a lot you can do with it.

The HS100 device doesn't have a published API, but with some excellent work from
the community, it's quite easy to address and control. Please see the references
section for more information.

## Build
Use the `build.sh` file to run a new build. The IP of the device is currently
hard coded into the `ac_control.py` file.

## Run
The build will go to `./dist/ac_control.app`. Run this and you'll get a new
status bar icon that can control the device.

![screenshot](docs/screenshot.png)

## References
* [Python](https://github.com/j05h/hs100)
* [Simple Script](https://github.com/natefox/tplink-hs100)
* [Bash](https://github.com/ggeorgovassilis/linuxscripts/blob/master/tp-link-hs100-smartplug/hs100.sh)
