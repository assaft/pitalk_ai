
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
* The micro USB power should be side-facing.
* The comopnents should be mounted to the top or sides of the box, not to the bottom.
* The bottom should be openable using screws, giving access to all components inside.
* The raspberry pi should be attached on one of the sides to allow easy access to the screen, speaker, microphone and button.
* A custom PCB board should be used to simplify connectivity and maintenance
* The PCB should connect to the Raspberry Pi GPIO interface using a
  2×20 male pin header.

## PCB Board requirements
* The board should not include the amplifier - it should include a female socket for the amplifier to be connected to it using a male header that was soldered to it. 
* The board should not include the microphone because the microphone is attached to the front of the device. The microphone will have pin header soldered to it.
* there should be board connectors on the pcb for connecting it to the microphone, speaker, button and screen; the screen connector should be keyed/locking.

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
| Gikfun 2" 4Ω 3W Speaker | 52.6 mm | 52.6 mm | 30 mm | Square frame |
| MAX98357 I2S Class-D Amplifier (breakout) | 19.4 mm | 17.8 mm | 3 mm | Adafruit-style breakout board |
| INMP441 Microphone (on 20 × 20 mm perfboard) | 20 mm | 20 mm | ~11 mm | Perfboard size per design spec; sensor itself is 4.7 × 3.8 × 1 mm |
| Momentary Push Button with LED | Ø 16–22 mm | — | ~39 mm | Circular; diameter depends on selected model (common: 16 mm or 22 mm panel cutout) |

# Box Arrangement

Two candidate front-face layouts. Scale: 1 char ≈ 5 mm.

## Layout 1 — Portrait (80 × 155 mm)

Screen on top, speaker in the middle, mic and button at the bottom.

```
╔══════════════════╗
║                  ║
║  ┌────────────┐  ║
║  │            │  ║
║  │   SCREEN   │  ║  58.8 × 37.1 mm
║  │            │  ║
║  └────────────┘  ║
║                  ║
║   ┌──────────┐   ║
║   │ ·  ·  ·  │   ║
║   │  ·  ·  · │   ║  52.6 × 52.6 mm
║   │ ·  ·  ·  │   ║
║   │  ·  ·  · │   ║
║   └──────────┘   ║
║                  ║
║   ◎         ◉    ║
║   mic       btn  ║
╚══════════════════╝
     80 × 155 mm
```

USB-C on the right side.

## Layout 4 — Landscape (150 × 80 mm)

Speaker on the left, screen on the right, mic and button below the screen.

```
╔══════════════════════════════════════╗
║                                      ║
║  ┌────────────┐  ┌────────────┐      ║
║  │ ·  ·  ·  · │  │            │      ║
║  │  ·  ·  ·   │  │   SCREEN   │      ║  58.8 × 37.1 mm
║  │ ·  ·  ·  · │  │            │      ║
║  │  ·  ·  ·   │  └────────────┘      ║
║  └────────────┘       ◎    ◉         ║
║                      mic   btn       ║
╚══════════════════════════════════════╝
  52.6 × 52.6 mm          150 × 80 mm
```

USB-C on the bottom edge (side of box). Button centered below screen, mic to its left.

## Internal Layout

### View from bottom

### View from the side


# PCB Design

Board: **76 mm × 58 mm**, four-layer, 1.6 mm FR4:

1. `F.Cu` — connector escapes and signals
2. `In1.Cu` — continuous ground plane
3. `In2.Cu` — secondary signal routing
4. `B.Cu` — signals and power

The authoritative wiring specification is [`pcb/pcb.md`](pcb/pcb.md). The
KiCad board is [`pcb/kicad/pitalk.kicad_pcb`](pcb/kicad/pitalk.kicad_pcb).
The matching schematic is
[`pcb/kicad/pitalk.kicad_sch`](pcb/kicad/pitalk.kicad_sch).

Regenerate it with:

```sh
.venv/bin/python pcb/kicad/build.py
.venv/bin/python pcb/kicad/build_schematic.py
```

## Connectors

| Ref | Footprint | Function |
|-----|-----------|----------|
| J1 | 2×20 2.54 mm male pin header | Raspberry Pi Zero 2W GPIO |
| J2 | JST GH SM15B 1.25 mm 1×15 male side-entry header | Waveshare 2" touch display |
| J3 | 1×7 2.54 mm female socket | MAX98357A amplifier module |
| J4, J5 | 1×3 2.54 mm male headers | INMP441 microphone |
| J6 | 1×4 2.54 mm male header | Momentary button + LED |

## GPIO Assignments (Raspberry Pi Zero 2W)

| Pin | GPIO | Net | Description |
|-----|------|-----|-------------|
| 1, 17 | 3V3 | +3V3 | Power |
| 2, 4 | 5V | +5V | Power (amp) |
| 3 | GPIO2 | I2C_SDA | Touch screen SDA |
| 5 | GPIO3 | I2C_SCL | Touch screen SCL |
| 7 | GPIO4 | TOUCH_INT | Touch interrupt |
| 12 | GPIO18 | I2S_BCLK | I2S bit clock (amp + mic) |
| 13 | GPIO27 | DISP_RST | Display reset |
| 15 | GPIO22 | BTN_SW | Button input |
| 19 | GPIO10 | SPI_MOSI | Display data |
| 22 | GPIO25 | DISP_DC | Display data/command |
| 23 | GPIO11 | SPI_SCLK | Display clock |
| 24 | GPIO8 | SPI_CE0 | Display chip select |
| 32 | GPIO12 | DISP_BL | Backlight PWM |
| 33 | GPIO13 | GPIO13 | LED drive (→ R1 → BTN_LED) |
| 35 | GPIO19 | I2S_LRCLK | I2S LR clock (amp + mic) |
| 38 | GPIO20 | I2S_DIN | I2S data from mic → RPi |
| 40 | GPIO21 | I2S_DOUT | I2S data RPi → amp |

## Passives

| Ref | Value | Purpose |
|-----|-------|---------|
| R1 | 330 Ω 0402 | BTN_LED current limiter (GPIO13 → LED) |
| C1 | 100 nF 0402 | +3V3 decoupling |
| C2 | 100 nF 0402 | +5V decoupling |


# Software code


# Todos 
* ~~Adding the component dimensions - width, height, depth - see section above.~~
* ~~Creating the box arrangment for organizing the components in a box - see section above.~~
* ~~Create a PCB board to simplify connections and maintenance - see section above.~~
* Writing the software for implementing the service.
