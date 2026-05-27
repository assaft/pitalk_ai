
# Introduction
This MD idescribes the creation of a device for recording, sending, receiving and playing vocal messages. 

## Device Goal
Enable easy voice messaging between kids. One click to start/end recording, one click to play an incoming. 

## Device Components
* Touch screen
* Microphone
* Speaker
* Amplifier
* System on chip - raspberry pi.
* Button with light
* PCB board, header cables, enclosure 

## Typical Use Case
Using the touch screen, user A can initiate a recording of a message to a particular pre-configured friend - user B. The microphone is used for the recording and a file is saved. Once user A presses to finish the recording, the file will be sent over the internet (using a Wifi connection), and reach the device of the recipient - user B. User B's device screen will show that there is an incoming message that hasn't been heard. Once user B presses on the screen to play it, the amplifier and speaker will be used to play it. 


# Requirements

## Functional Requirements
* A user can record a new message and send it to one of his/her friends. 
* A user can browse old messages he/she received and listen to them.
* A user can have a custom different list of friends - each user a different list 
* The list of friends per user should be editable.

## System Requirements
* The device should support reboot, shut down, turn on
* The device should have a Wifi access point mode so smartphones can connect to itto configure the Wifi network.

## Package Engineering Requirements
* The device should be packaged in a compact box
* The device should only have one external connection for power
* The screen, speaker, microphone and button should be front facing.
* The USB-C power power should be side-facing.
* The comopnents should be mounted to the top or sides of the box, not to the bottom.
* The bottom should be openable using screws, giving access to all components inside.
* The raspberry pi should be attached on one of the sides to allow easy access to the screen, speaker, microphone and button.
* A custom PCB board should be used to simplify connectivity and maintenance
* The PCB should connect to the Raspberry PI using a pin header. 

## PCB Board requirements
* The board may include the amplifier as part of it.
* The board should not include the microphone because the microphone is attached to the front of the device.
* there should be pin headers on the pcb for connecting it to the microphone, speaker, button and screen.

# Components

## Models
1. Controller: Raspberry Pi Zero 2W
2. Screen: Waveshare 2 inch Capacitive Touch Display Module (ST7789T3, CST816D)
3. Speaker: Gikfun 2 inch 4Ohm 3W Full Range Audio Speaker Stereo Woofer Loudspeaker
4. Amplifier: Max98357 I2S 3W Class D Amplifier
5. Microphone: INMP441 Omnidirectional Microphone attached over a Perfboard PCB of 2cm x 2cm
7. Button: momentary push button with led light

## Dimensions

| Component | Length | Width | Depth / Thickness | Notes |
|-----------|--------|-------|-------------------|-------|
| Raspberry Pi Zero 2W | 65 mm | 30 mm | ~5 mm | Board only; add ~2 mm for protruding micro-SD card |
| Waveshare 2" Capacitive Touch LCD (ST7789T3 / CST816D) | 58.8 mm | 37.1 mm | ~4 mm | PCB size; active display area is 40.8 × 30.6 mm |
| Gikfun 2" 4Ω 3W Speaker | Ø 50.8 mm | — | 30 mm | Circular; diameter = 50.8 mm (2"), depth = 30 mm |
| MAX98357 I2S Class-D Amplifier (breakout) | 19.4 mm | 17.8 mm | 3 mm | Adafruit-style breakout board |
| INMP441 Microphone (on 20 × 20 mm perfboard) | 20 mm | 20 mm | ~11 mm | Perfboard size per design spec; sensor itself is 4.7 × 3.8 × 1 mm |
| Momentary Push Button with LED | Ø 16–22 mm | — | ~39 mm | Circular; diameter depends on selected model (common: 16 mm or 22 mm panel cutout) |

# Box Arragement

## Front layout


## Internal Layour

### View from bottom

### View from the side


# PCB Design


# Software code


# Todos 
* ~~Adding the component dimensions - width, height, depth - see section above.~~
* Creating the box arrangment for organizing the components in a box - see section above.
* Create a PCB board to simplify connections and maintenance - see section above.
3. Writing the software for implementing the service.


