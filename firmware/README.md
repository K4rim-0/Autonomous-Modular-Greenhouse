Firmware, the thing that makes this project tick.

I used micropython and the Thonny IDE to program the rp2040 zero.

I aimed to make the code as object orientated as possible, hence the multiple classes.
When starting this project, I was considering the use of a menu library, however after failing to understand how to use them I set this project aside for a long time until gaining some knowledge on coding from the courses I took and learning of the various concepts involved.

The code you currently see is the second variant, my first code used while loops to stay inside menu  which is blocking, meaning all code beyond the active while loop is never read.
In some applications this may have been acceptable, but in this case it could risk for instance over watering (by running water pump) as the code to check elapsed time never gets read to turn off the pump.

To make the code non blocking I decided to give each menu a number (identifier) so to track which menu should be displayed when user presses the encoder. There user can set parameters (temperature, humidity, etc.) or test components.

Some notable learning points from this project are to only "print()" the OLED screen when there has been a change, since it can cause quite a delay to responsiveness if it is set to continuously update.
Same goes for reading sensor, I set them to be read once every 5 seconds. Point is execute code or instructions when it is needed to avoid taking up processing power from the microcontroller.
Also, the rp2040 has two cores, so it is possible to split up the load among the two cores to increase responsiveness, though I personally haven't done this. This project has already taken long enough.

A slightly silly mistake that set me back was connecting the digital reading from the DHT22 to an analogue pin and causing leakage to other neighboring pins on the rp2040 zero and leading to a faulty reading from capacitive soil moisture sensor (connected to analogue pin).
