# PiTalk PCB — Pre-Manufacturing Validation

Date: 2026-06-24

## Release status

**Conditional — suitable for prototype fabrication after the mechanical and
cable checks listed under “Remaining gates.”**

The electrical design and generated fabrication data pass the automated and
document-based checks that can be performed without physical parts or a
selected PCB manufacturer.

## Automated KiCad checks

| Check | Result |
|-------|--------|
| Schematic ERC | PASS — 0 violations |
| PCB DRC | PASS — 0 violations |
| Unconnected PCB items | PASS — 0 |
| Schematic/PCB parity | PASS — 0 issues |
| Gerber export | PASS |
| PTH/NPTH drill export | PASS |
| Footprint pad geometry vs installed KiCad libraries | PASS |

Reports:

- [`erc.json`](erc.json)
- [`drc-with-parity.json`](drc-with-parity.json)
- [`board-statistics.rpt`](board-statistics.rpt)

## Datasheet and pinout audit

### Raspberry Pi GPIO

The physical GPIO pin assignments match the standard Raspberry Pi 40-pin
header: SPI0, I2C1, PCM/I2S, power, and ground are mapped to the expected
physical pins.

Source:
[Raspberry Pi GPIO documentation](https://pip.raspberrypi.com/categories/685-whitepapers-app-notes/documents/RP-003613-WP/Using-gpio-pins.pdf)

### Waveshare 2-inch display

SPI, touch I2C, reset, interrupt, power, and ground match Waveshare's Raspberry
Pi table. `LCD_BL` is intentionally moved from BCM18 to BCM12 because BCM18 is
used as the I2S bit clock. Software must configure the display backlight as
BCM12.

J2 uses the male JST GH `SM15B-GHS-TB` side-entry footprint.

Source:
[Waveshare 2inch Capacitive Touch LCD](https://www.waveshare.com/wiki/2inch_Capacitive_Touch_LCD)

### MAX98357A amplifier module

The documented module photo confirms the seven-pin order:
`LRC, BCLK, DIN, GAIN, SD, GND, VIN`.

The 5 V supply is within the MAX98357A 2.5–5.5 V range. A 4 Ω speaker is
supported. The amplifier can draw approximately 650 mA at high output;
Adafruit recommends allowing at least 800 mA supply capacity for the amplifier.

C1 provides 10 µF bulk bypass capacitance near J3. The MAX98357A datasheet
specifies a 10 µF bypass capacitor and recommends additional bulk capacitance
for long supply paths. The selected breakout module also contains local
decoupling.

Sources:

- [MAX98357A datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf)
- [Adafruit MAX98357A pinout and power guidance](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts)

### INMP441 microphone module

The two three-pin headers match the module silkscreen:
`SD, VDD, GND` and `L/R, WS, SCK`. VDD is 3.3 V, and L/R is tied to ground to
select the left channel. BCLK and LRCLK are shared with the amplifier, while
the microphone uses the Pi PCM data-input net.

Only the pictured module/header arrangement is validated. INMP441 breakout
boards from different sellers are not mechanically standardized.

### Button and LED

The switch returns to ground and requires the Pi GPIO's internal pull-up to be
enabled in software. The LED is driven through 330 Ω. With a typical LED
forward voltage, GPIO current is approximately 3–5 mA, comfortably below the
Pi GPIO limit.

## Layout, power, and signal review

- Four-layer stack: `F.Cu / GND / signal / B.Cu`.
- In1 is a continuous ground plane with no routed signal splits.
- SPI clock and I2S bit clock are routed on F.Cu adjacent to the ground plane.
- The microphone connectors are separated from the amplifier connector.
- The amplifier bulk capacitor is close to the amplifier's 5 V input.
- Minimum track width: 0.25 mm.
- Power-track width: 0.40 mm.
- Minimum measured copper clearance: 0.31 mm.
- Through-vias: 0.60 mm diameter with 0.30 mm drills.
- Mounting holes: four 3.20 mm NPTH holes.
- Conservative resistance estimate for the entire 92 mm, 0.40 mm-wide 5 V
  copper network at 1 oz is about 0.11 Ω. At 650 mA this is about 72 mV drop;
  the actual Pi-to-amplifier path is shorter than the total network.

These dimensions are within common four-layer PCB capabilities.

## Gerber and drill inspection

Visual inspection files are in [`inspection/`](inspection/).

- F.Cu: PASS
- In1.Cu ground plane: PASS, continuous
- In2.Cu: PASS
- B.Cu: PASS
- PTH drill map: PASS
- NPTH drill map: PASS
- Board outline and four mounting holes: PASS

Fabrication files are in [`fabrication/`](fabrication/).

## Remaining gates

These cannot be closed from CAD files alone:

1. **J1 mating system:** confirm the exact female cable/socket that mates with
   the unshrouded 2×20 male header. Verify pin 1 at both ends and ensure the
   connector cannot be installed reversed.
2. **J2 cable assembly:** confirm a 15-position female-to-female JST GH cable
   and verify whether the harness is pin-for-pin or reversed when viewed from
   the mating faces.
3. **Microphone fit:** measure the actual center-to-center spacing and pin
   orientation of the purchased INMP441 module or its 20×20 mm carrier.
4. **Amplifier fit:** place the exact purchased module over a 1:1 print and
   verify body, speaker-terminal, and capacitor clearance.
5. **Component specification:** C1 must be rated at least 6.3 V; 10 V is
   preferred. Confirm polarity during assembly.
6. **Power budget:** the complete device power supply must cover the Pi,
   display, amplifier peaks, microphone, and margin. A weak Pi supply can cause
   undervoltage during loud audio.
7. **Manufacturer DFM:** select the fabricator and map this design to its stock
   1.6 mm four-layer stack-up. No controlled impedance is required, so the
   dielectric dimensions may be adapted to the manufacturer's standard stack.
8. **Physical prototype tests:** continuity, rail shorts, idle current, display
   SPI, touch I2C, microphone capture, amplifier playback, button, LED, and
   noise testing remain mandatory on the first assembled boards.

