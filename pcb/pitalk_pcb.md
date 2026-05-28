# PiTalk PCB Design

## Overview

Custom PCB that sits between all front-panel components and the Raspberry Pi Zero 2W.
Connects to the RPi with a 40-pin IDC ribbon cable between shrouded 2×20 headers.
Includes the MAX98357 I2S amplifier on-board; all other components connect via headers.

**Board size:** 65 × 55 mm  
**Layers:** 2  
**Connector style:** 2.54 mm board connectors; keyed/locking where practical  

---

## Connectors & Components

| Ref | Part | Description |
|-----|------|-------------|
| J1  | 2×20 shrouded male IDC header, 2.54 mm | GPIO ribbon-cable connector to RPi Zero 2W |
| J2  | 1×15 keyed locking connector, 2.54 mm | Screen (Waveshare 2" SPI + I2C), Molex SL-style |
| J3  | 2×3 male pin header, 2.54 mm | Microphone (INMP441) — use female-to-female header cable |
| J4  | 1×2 screw terminal, 5.0 mm | Speaker output |
| J5  | 1×4 pin header, 2.54 mm | Button (switch + LED) |
| U1  | MAX98357A (WLCSP) | I2S Class-D mono amplifier |
| C1  | 100 nF, 0402 | VDD bypass cap for U1 |
| C2  | 10 µF, 0402 | Bulk decoupling on 3.3 V rail |
| R1  | 330 Ω, 0402 | Current limit for button LED |

---

## Pin Mapping — J1 (40-pin GPIO) to Signals

| Physical Pin | BCM GPIO | Signal | Destination |
|-------------|----------|--------|-------------|
| 1  | 3.3 V | VCC_3V3 | U1 VDD, J2, J3 |
| 2  | 5 V   | VCC_5V  | (spare) |
| 3  | GPIO2 | I2C_SDA | J2 pin 10 (touch SDA) |
| 5  | GPIO3 | I2C_SCL | J2 pin 11 (touch SCL) |
| 6  | GND   | GND | Common ground |
| 8  | GPIO14 | — | NC |
| 11 | GPIO17 | BTN_SW  | J5 pin 1 (switch) |
| 12 | GPIO18 | I2S_BCLK | U1 BCLK, J3 pin 4 (SCK) |
| 13 | GPIO27 | BTN_LED | R1 → J5 pin 3 (LED+) |
| 19 | GPIO10 | SPI_MOSI | J2 pin 5 |
| 21 | GPIO9  | SPI_MISO | NC (display is write-only) |
| 22 | GPIO25 | DISP_INT | J2 pin 12 (touch INT) |
| 23 | GPIO11 | SPI_SCLK | J2 pin 6 |
| 24 | GPIO8  | SPI_CE0  | J2 pin 7 (display CS) |
| 25 | GND    | GND | — |
| 26 | GPIO7  | DISP_DC  | J2 pin 8 |
| 31 | GPIO6  | DISP_RST | J2 pin 9 |
| 35 | GPIO19 | I2S_LRCLK | U1 LRCLK, J3 pin 5 (WS) |
| 38 | GPIO20 | I2S_DIN  | J3 pin 6 (SD — mic data in) |
| 40 | GPIO21 | I2S_DOUT | U1 DIN |

---

## J2 — Screen Connector Pinout (1×15 keyed locking, 2.54 mm)

| Pin | Signal | Notes |
|-----|--------|-------|
| 1  | GND | |
| 2  | VCC (3.3 V) | |
| 3  | GND | |
| 4  | VCC (3.3 V) | |
| 5  | MOSI | SPI data |
| 6  | SCLK | SPI clock |
| 7  | CS | SPI chip select (CE0) |
| 8  | DC | Data/command |
| 9  | RST | Display reset |
| 10 | SDA | I2C touch data |
| 11 | SCL | I2C touch clock |
| 12 | INT | Touch interrupt |
| 13 | BL  | Backlight (tie to 3.3 V) |
| 14 | GND | |
| 15 | VCC (3.3 V) | |

---

## J3 — Microphone Connector Pinout (2×3 male header, 2.54 mm)

Matches the INMP441 perfboard's 2×3 pin grid.
Connect with **two 3-pin female-to-female Dupont/header cables**: cable A = power row, cable B = signal row.
The PCB assembly should include the male 2×3 header soldered into J3.
Build the microphone perfboard with the same split and order: one 3-pin male header for `VDD`, `GND`, `L/R`, and one 3-pin male header for `SCK`, `WS`, `SD`.

```
       Col 1      Col 2      Col 3
Row A  pin 1      pin 2      pin 3
(pwr)  VDD 3.3V   GND        GND (L/R → left ch)

Row B  pin 4      pin 5      pin 6
(sig)  I2S_BCLK   I2S_LRCLK  I2S_DIN
       SCK        WS         SD
```

---

## J5 — Button Connector Pinout (1×4, 2.54 mm)

| Pin | Signal | Notes |
|-----|--------|-------|
| 1  | BTN_SW | Switch signal (GPIO17, internal pull-up) |
| 2  | GND | Switch return |
| 3  | BTN_LED | LED anode (via R1 330 Ω) |
| 4  | GND | LED cathode |

---

## U1 — MAX98357A Connections

| Pin | Net | Notes |
|-----|-----|-------|
| VDD | 3.3 V | + C1 100 nF to GND |
| GND | GND | |
| BCLK | I2S_BCLK | |
| LRCLK | I2S_LRCLK | |
| DIN | I2S_DOUT | RPi GPIO21 |
| SD_MODE | 3.3 V | Always-on (tied high) |
| GAIN | NC | Float = 15 dB |
| OUT+ | J4 pin 1 | Speaker + |
| OUT- | J4 pin 2 | Speaker − |

---

## Component Placement (top view, 65 × 55 mm board)

```
┌─────────────────────────────────────────────────────────────┐ 65mm
│ ●                                                         ● │ ← mounting holes
│                                                             │
│ [J2 — Screen 15-pin locking ──────────] [J3 — Mic male 2×3] │ ← top edge
│                                                             │
│ [J4]                                                        │
│  Spk          [U1 MAX98357] [C1][C2]                        │
│ [J5]                                                        │
│  Btn     [R1]                                               │
│                                                             │
│ ● [J1 — GPIO 40-pin shrouded IDC header ────────────────] ● │ ← bottom edge
└─────────────────────────────────────────────────────────────┘
                                                          55mm↕
```

---

## Design Notes

- All I2S signals (BCLK, LRCLK) are shared between the MAX98357 amplifier (output) and the INMP441 microphone (input); the RPi drives the clock lines for both.
- The microphone L/R pin is tied to GND on J3 pin 3 to select the left audio channel.
- MAX98357 SD_MODE is tied high (3.3 V) to keep the amp always enabled; the RPi can mute by sending silence over I2S.
- Backlight (J2 pin 13) is hard-wired to 3.3 V. Add a PWM GPIO connection if dimming is needed in a future revision.
- R1 (330 Ω) limits LED current to ≈ 10 mA at 3.3 V.
