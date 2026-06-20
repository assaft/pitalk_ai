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

![Waveshare 2" Capacitive Touch LCD pinout (15-pin header)](images/waveshare-2inch-lcd-pinout.jpg)

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

![MAX98357A I2S Class-D mono amplifier module](images/max98357a-amplifier.jpg)

The `accessory_pin_id` numbering follows the module's 1×7 header order
(`LRC`, `BCLK`, `DIN`, `GAIN`, `SD`, `GND`, `VIN`).

| pi_pin | pi_bcm | accessory_pin | accessory_pin_id |
|-------:|--------|---------------|-----------------:|
| 35 | BCM19 (PCM_FS)  | lrc (lr / word clock)              | 1 |
| 12 | BCM18 (PCM_CLK) | bclk (bit clock)                   | 2 |
| 40 | BCM21 (PCM_DOUT)| din (i2s data in)                  | 3 |
| —  | — (not connected) | gain (gain select)               | 4 |
| —  | — (not connected) | sd (shutdown / channel select)   | 5 |
| 6  | GND           | gnd                                  | 6 |
| 2  | 5V            | vin (5v)                             | 7 |

> Accessory pins **4** (`GAIN`) and **5** (`SD`, shutdown/channel-select) are
> set on the module/board (not driven by the Pi) — both shown mapping to
> nothing above. Default: `GAIN` floating (+9 dB), `SD` pulled to enable
> stereo-averaged mono output.

### PCB Connector

2.54mm 7pin socket

![2.54 mm 1×7 female header socket](images/socket-2.54mm-7pin.jpg)

✅ **Verified**

---

## Microphone — INMP441 I2S MEMS

Sends audio to the Pi over the same I2S/PCM bus (shares BCLK and LRCLK with
the amplifier; uses the PCM data-in line). Connects via a board header.

![INMP441 I2S MEMS microphone module](images/inmp441-microphone.jpg)

The `accessory_pin_id` numbering follows the module's two 3-pin headers,
left-to-right: header 1 is `SD`, `VDD`, `GND`; header 2 is `L/R`, `WS`, `SCK`.

| pi_pin | pi_bcm | accessory_pin | accessory_pin_id |
|-------:|--------|---------------|-----------------:|
| 38 | BCM20 (PCM_DIN)| sd (i2s data out)                   | 1 |
| 1  | 3V3            | vdd (v3.3)                          | 2 |
| 9  | GND            | gnd                                 | 3 |
| —  | — (tied to gnd)| l/r (channel select → gnd = left)   | 4 |
| 35 | BCM19 (PCM_FS) | ws (word select)                    | 5 |
| 12 | BCM18 (PCM_CLK)| sck (bit clock)                     | 6 |

> Accessory pin **4** (`L/R`) is a static channel-select input, not a signal
> the Pi drives — tying it to `gnd` selects the left channel. Make this tie on
> the **PCB**, not on the mic module: in the KiCad schematic, connect the
> `L/R` pin to a `GND` power symbol (same net as the mic's own `gnd`), then let
> the board's ground pour realize it in copper. The mic module solders onto the
> headers straight through, unmodified — do **not** short `L/R` to `gnd` on the
> module. Shown mapping to nothing above because no Pi pin is involved.

### PCB Connector

2.54mm 1×3 male pin header (×2)

Two 2.54mm 1×3 male pin headers. The six accessory pins are split across the
two headers in `accessory_pin_id` order — pins 1–3 on the first header, pins
4–6 on the second. Pin order below is left-to-right, matching the module.

![2.54 mm 1×3 male pin header](images/male-header-2.54mm-3pin.jpg)

```
Header A (1×3 male)          Header B (1×3 male)
┌───┬───┬───┐                ┌───┬───┬───┐
│ ▯ │ ▯ │ ▯ │                │ ▯ │ ▯ │ ▯ │
└───┴───┴───┘                └───┴───┴───┘
  1   2   3                    4   5   6
 sd  vdd gnd                 l/r  ws  sck
```

| header | pins (left-to-right) | accessory_pin_id |
|--------|----------------------|------------------|
| A | sd, vdd, gnd  | 1, 2, 3 |
| B | l/r, ws, sck  | 4, 5, 6 |

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

### PCB Connector

2.54mm 1×4 male pin header

A single 2.54mm 1×4 male pin header carries all four button signals,
left-to-right: `sw`, `sw_gnd`, `led+`, `led-`.

![2.54 mm 1×4 male pin header](images/male-header-2.54mm-4pin.jpg)

```
1×4 male header
┌────┬────────┬──────┬──────┐
│ ▯  │   ▯    │  ▯   │  ▯   │
└────┴────────┴──────┴──────┘
  1       2       3      4
  sw    sw_gnd   led+   led-
```

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

---

## PCB Board

The carrier PCB must provide the following connectors, one per interface
(detailed in each accessory section above):

| # | Interface | Connector | Pins |
|--:|-----------|-----------|-----:|
| 1 | Raspberry Pi Zero 2W | 2×20 2.54mm female header (mounts onto the Pi 40-pin header) | 40 |
| 2 | Display (Waveshare 2" Touch) | JST GH1.25 1×15 | 15 |
| 3 | Amplifier (MAX98357A) | 2.54mm 1×7 female socket | 7 |
| 4 | Microphone (INMP441) | 2.54mm 1×3 male pin header (×2) | 3 + 3 |
| 5 | Button (push button + LED) | 2.54mm 1×4 male pin header | 4 |

> The speaker is **not** a PCB connector — it wires directly to the
> amplifier's output (see the Speaker section), not to the carrier board.
