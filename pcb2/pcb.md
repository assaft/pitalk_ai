# PiTalk PCB (pcb2) — Pin Connections

This document defines the electrical pin mapping for the PiTalk carrier PCB,
designed from scratch around the **Raspberry Pi Zero 2W** 40-pin header.

Each accessory gets its own section with a pin-mapping table. Columns:

| Column | Meaning |
|--------|---------|
| `pi_pin` | Physical pin number on the Pi 40-pin header (1–40) |
| `pi_bcm` | Broadcom GPIO number (BCMxx), or the power rail name for power/ground pins |
| `accessory_pin` | Signal/function on the accessory side (e.g. `gnd`, `v3.3`, `clock`) |

> Buses are shared where the hardware requires it: SPI0 drives the display,
> I2C1 drives the touch controller, and the I2S/PCM bus is shared by the
> amplifier (output) and microphone (input).

---

## Raspberry Pi Zero 2W — 40-pin header reference

For convenience, the full header pinout this design draws from:

| pi_pin | pi_bcm | pi_pin | pi_bcm |
|-------:|--------|-------:|--------|
| 1  | 3V3        | 2  | 5V          |
| 3  | BCM2 (SDA1)| 4  | 5V          |
| 5  | BCM3 (SCL1)| 6  | GND         |
| 7  | BCM4       | 8  | BCM14 (TXD) |
| 9  | GND        | 10 | BCM15 (RXD) |
| 11 | BCM17      | 12 | BCM18 (PCM_CLK) |
| 13 | BCM27      | 14 | GND         |
| 15 | BCM22      | 16 | BCM23       |
| 17 | 3V3        | 18 | BCM24       |
| 19 | BCM10 (MOSI)| 20 | GND        |
| 21 | BCM9 (MISO)| 22 | BCM25       |
| 23 | BCM11 (SCLK)| 24 | BCM8 (CE0) |
| 25 | GND        | 26 | BCM7 (CE1)  |
| 27 | BCM0 (ID_SD)| 28 | BCM1 (ID_SC)|
| 29 | BCM5       | 30 | GND         |
| 31 | BCM6       | 32 | BCM12       |
| 33 | BCM13      | 34 | GND         |
| 35 | BCM19 (PCM_FS)| 36 | BCM16     |
| 37 | BCM26      | 38 | BCM20 (PCM_DIN) |
| 39 | GND        | 40 | BCM21 (PCM_DOUT)|

---

## Display — Waveshare 2" Capacitive Touch (ST7789T3 + CST816D)

Single module combining an SPI display (ST7789T3) and an I2C capacitive
touch controller (CST816D). Driven by SPI0 (display) and I2C1 (touch).
Pin mapping follows the "Working with Raspberry Pi" table on the
[Waveshare 2inch Capacitive Touch LCD wiki](https://www.waveshare.com/wiki/2inch_Capacitive_Touch_LCD).
The `accessory_pin_id` numbering follows the module's
[pinout diagram](https://www.waveshare.com/img/devkit/LCD/2inch-Capacitive-Touch-LCD/2inch-Capacitive-Touch-LCD-details-9.jpg)
(the 15-pin header).

| pi_pin | pi_bcm | accessory_pin | accessory_pin_id |
|-------:|--------|---------------|-----------------:|
| 17 | 3V3          | vcc (v3.3)                                         | 1  |
| —  | — (not connected) | 3v3 (on-module regulator output)                   | 2  |
| 25 | GND          | gnd                                                | 3  |
| 21 | BCM9 (MISO)  | miso (spi miso)                                    | 4  |
| 19 | BCM10 (MOSI) | mosi (spi data in)                                 | 5  |
| 23 | BCM11 (SCLK) | sclk (spi clock)                                   | 6  |
| —  | — (not connected) | sd_cs (on-module sd slot)                          | 7  |
| 24 | BCM8 (CE0)   | lcd_cs (display chip select)                       | 8  |
| 22 | BCM25        | lcd_dc (data/command)                              | 9  |
| 13 | BCM27        | lcd_rst (display reset)                            | 10 |
| 32 | BCM12        | lcd_bl (backlight) — remapped from BCM18, see note | 11 |
| 3  | BCM2 (SDA1)  | tp_sda (touch i2c data)                            | 12 |
| 5  | BCM3 (SCL1)  | tp_scl (touch i2c clock)                           | 13 |
| 7  | BCM4         | tp_int (touch interrupt)                           | 14 |
| 11 | BCM17        | tp_rst (touch reset)                               | 15 |

> Accessory pins **2** (`3V3`, the on-module regulator output) and **7**
> (`SD_CS`, the micro-SD slot's chip select) are left unconnected on this board
> — both shown mapping to nothing above.
>
> 🔧 **Backlight remapped:** the Waveshare default wires `LCD_BL` to **BCM18**,
> which is also `PCM_CLK` (I2S BCLK) used by the amplifier and microphone below.
> Since BCM18 cannot serve both, `LCD_BL` is remapped on this board to
> **BCM12 (pin 32)** — a hardware-PWM-capable pin — freeing BCM18 for I2S.
> This requires routing `LCD_BL` to pin 32 on the PCB (not pin 12) and setting
> the backlight GPIO to BCM12 in software.

### PCB Connector

JST GH1.25 15p

![JST GH1.25 15-pin connector (shown on the Waveshare module)](images/jst-gh-15p-connector.jpg)

✅ **Verified**

---

## Amplifier — MAX98357A I2S Class-D (3W)

Receives audio from the Pi over the I2S/PCM bus. Mounted on the PCB via a
female socket (per board requirements). Speaker connects to its output.

| pi_pin | pi_bcm | accessory_pin |
|-------:|--------|---------------|
| 2  | 5V            | vin (5v)            |
| 6  | GND           | gnd                 |
| 12 | BCM18 (PCM_CLK) | bclk (bit clock)  |
| 35 | BCM19 (PCM_FS)  | lrc (lr / word clock) |
| 40 | BCM21 (PCM_DOUT)| din (i2s data in) |

> `GAIN` and `SD` (shutdown/channel-select) pins are set on the module/board
> (not driven by the Pi). Default: `GAIN` floating (+9 dB), `SD` pulled to
> enable stereo-averaged mono output.

### PCB Connector

2.54mm 7pin socket

![2.54 mm 1×7 female header socket](images/socket-2.54mm-7pin.jpg)

✅ **Verified**

---

## Microphone — INMP441 I2S MEMS

Sends audio to the Pi over the same I2S/PCM bus (shares BCLK and LRCLK with
the amplifier; uses the PCM data-in line). Connects via a board header.

| pi_pin | pi_bcm | accessory_pin |
|-------:|--------|---------------|
| 1  | 3V3            | vdd (v3.3)         |
| 9  | GND            | gnd                |
| 12 | BCM18 (PCM_CLK)| sck (bit clock)    |
| 35 | BCM19 (PCM_FS) | ws (word select)   |
| 38 | BCM20 (PCM_DIN)| sd (i2s data out)  |

> `L/R` channel-select pin is tied to `gnd` on the board (left channel).

✅ **Verified**

---

## Speaker — Gikfun 2" 4Ω 3W

The speaker does **not** connect to the Pi header. It connects to the
amplifier's bridge-tied output via a 2-pin board connector.

| amp_pin | accessory_pin |
|---------|---------------|
| out+ | speaker + |
| out- | speaker - |

✅ **Verified**

---

## Button — Momentary push button with LED

Switch contact reads as a GPIO input; the LED is driven through an on-board
series current-limiting resistor.

| pi_pin | pi_bcm | accessory_pin |
|-------:|--------|---------------|
| 15 | BCM22 | sw (switch input)        |
| 34 | GND   | sw_gnd (switch return)   |
| 33 | BCM13 | led+ (via series resistor) |
| 39 | GND   | led- (led cathode)       |

---

## Full wiring

Consolidated view of every Raspberry Pi pin and which accessory pin it
connects to. `—` means that accessory does not use the pin. Power and ground
rails span several physical header pins; the per-component sections above list
the specific pins used.

Rows are one physical pin each. Where an accessory shares a rail (3V3, GND),
a separate header pin is allocated per accessory so every connection maps to a
single pin. (BCM18/BCM19 are genuine shared signal nets and stay on one pin.)

| pi_pin | pi_bcm | display | amplifier | microphone | button |
|-------:|--------|---------|-----------|------------|--------|
| 1  | 3V3             | —        | —    | vdd  | —      |
| 2  | 5V              | —        | vin  | —    | —      |
| 3  | BCM2 (SDA1)     | tp_sda   | —    | —    | —      |
| 5  | BCM3 (SCL1)     | tp_scl   | —    | —    | —      |
| 6  | GND             | —        | gnd  | —    | —      |
| 7  | BCM4            | tp_int   | —    | —    | —      |
| 9  | GND             | —        | —    | gnd  | —      |
| 11 | BCM17           | tp_rst   | —    | —    | —      |
| 12 | BCM18 (PCM_CLK) | —        | bclk | sck  | —      |
| 13 | BCM27           | lcd_rst  | —    | —    | —      |
| 15 | BCM22           | —        | —    | —    | sw     |
| 17 | 3V3             | vcc      | —    | —    | —      |
| 19 | BCM10 (MOSI)    | mosi     | —    | —    | —      |
| 21 | BCM9 (MISO)     | miso     | —    | —    | —      |
| 22 | BCM25           | lcd_dc   | —    | —    | —      |
| 23 | BCM11 (SCLK)    | sclk     | —    | —    | —      |
| 24 | BCM8 (CE0)      | lcd_cs   | —    | —    | —      |
| 25 | GND             | gnd      | —    | —    | —      |
| 32 | BCM12           | lcd_bl   | —    | —    | —      |
| 33 | BCM13           | —        | —    | —    | led+   |
| 34 | GND             | —        | —    | —    | sw_gnd |
| 35 | BCM19 (PCM_FS)  | —        | lrc  | ws   | —      |
| 38 | BCM20 (PCM_DIN) | —        | —    | sd   | —      |
| 39 | GND             | —        | —    | —    | led-   |
| 40 | BCM21 (PCM_DOUT)| —        | din  | —    | —      |

> **Unused header pins** (not connected on this board):
> 4 (5V), 8 (BCM14/TXD), 10 (BCM15/RXD), 14 (GND), 16 (BCM23), 18 (BCM24),
> 20 (GND), 26 (BCM7/CE1), 27 (BCM0/ID_SD), 28 (BCM1/ID_SC), 29 (BCM5),
> 30 (GND), 31 (BCM6), 36 (BCM16), 37 (BCM26).

✅ **Verified**
