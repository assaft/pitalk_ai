# PiTalk PCB — Independent Verification Report

**Reviewer pass date:** 2026-06-27
**Scope:** schematic, netlist, PCB, DRC/ERC, layout, datasheet pinouts.
**Sources reviewed:** `pcb.md`, `kicad/pitalk.kicad_sch`, `kicad/pitalk.kicad_pcb`,
`kicad/pitalk.net.xml`, `kicad/erc.json`, `kicad/drc-with-parity.json`,
`kicad/board-statistics.rpt`, `kicad/PRE_MANUFACTURING_VALIDATION.md`.

## Methodology

The intended netlist was reconstructed by hand from `pcb.md` and compared
node-by-node against the KiCad-exported netlist (`pitalk.net.xml`). Footprints,
the PCB stackup/zones/outline, and the automated ERC/DRC/parity reports were
then independently cross-checked. No KiCad, Python, or PCB design files were
modified during this review. Two documentation findings (#1, #3 below) were
corrected in `pcb.md`.

---

## 1. Electrical netlist — cross-checked against `pcb.md` ✅

Every signal net matches the spec. All 21 functional nets verified:

| Net | Pi pin(s) | Accessory | Verdict |
|---|---|---|---|
| SPI_MOSI/MISO/SCLK | 19/21/23 | J2 5/4/6 | ✅ |
| LCD_CS/DC/RST | 24/22/13 | J2 8/9/10 | ✅ |
| LCD_BL | 32 (BCM12) | J2 11 | ✅ remap from BCM18 honored |
| TP_SDA/SCL/INT/RST | 3/5/7/11 | J2 12/13/14/15 | ✅ |
| I2S_BCLK | 12 (BCM18) | J3 2 + J5 3 | ✅ shared amp+mic |
| I2S_LRCLK | 35 (BCM19) | J3 1 + J5 2 | ✅ shared amp+mic |
| AMP_DIN | 40 (DOUT) | J3 3 | ✅ |
| MIC_SD | 38 (DIN) | J4 1 | ✅ full-duplex I2S correct |
| BTN_SW / LED_A | 15 / 33→R1→J6 3 | J6 1 | ✅ 330 Ω in series |
| +3V3 | 1, 17 | J2 1, J4 2 | ✅ |
| +5V | 2 | J3 7, C1+ | ✅ |
| GND | 6,9,14,20,25,30,34,39 | all module grounds, C1− | ✅ |

- **I2S bus conflict avoidance is correct.** BCM18 is freed for the I2S bit
  clock and the backlight is genuinely moved to BCM12 (pin 32) in the netlist —
  the most error-prone part of this design is done right.
- **C1 polarity correct:** pin 1 (+) → +5V, pin 2 (−) → GND.
- **No double-driven pins / no shorts:** every pad appears in exactly one net.
- No-connects match spec: J2.2, J2.7 (module 3V3-out, SD_CS) and J3.4, J3.5
  (GAIN, SD) are NC.

## 2. Automated checks — independently confirmed ✅

- **ERC:** 0 violations. All global labels have a matching partner (each named
  net verified to have ≥2 nodes — no orphan/typo labels).
- **DRC:** 0 violations, 0 unconnected items, **0 schematic/PCB parity issues** —
  the board matches the schematic.
- Min clearance 0.385 mm, min track 0.25 mm, min drill 0.30 mm — all
  comfortably manufacturable.

## 3. Physical / layout — confirmed from the PCB file ✅

- **76 × 58 mm** outline confirmed (Edge.Cuts forms a clean closed rectangle
  0,0 → 76,58).
- **4-layer stack** `F.Cu / In1.Cu (power) / In2.Cu (signal) / B.Cu`, 1.6 mm.
- **In1.Cu is a single continuous GND pour** (one zone, filled, spanning the
  full board with thermal reliefs and mounting-hole keepouts) — no split planes.
  Signals route on F/In2/B (98/34/32 segments). Proper reference plane.
- 4× 3.2 mm NPTH mounting holes present.
- Footprints all match the spec: J2 = side-entry SMD JST GH SM15B; J3 =
  **female** PinSocket 1×07 (matches "socket" requirement); mic on two 1×03
  headers; pad/drill counts reconcile (61 THT + 17 SMD/J2 + 4 NPTH).

---

## Findings

**🟢 1 — RESOLVED — Doc/design mismatch on GND pins 20 & 30.**
The schematic ties **all 8** Pi ground pins (6, 9, 14, 20, 25, 30, 34, 39) to
GND, while `pcb.md` previously listed pins 20 and 30 as "not connected." The
schematic's choice is electrically *better* (more ground returns). **Fixed in
`pcb.md`:** pins 20 and 30 are now shown as GND rows in the full-wiring table,
removed from the "Unused header pins" list, and a note clarifies that all eight
Pi ground pins tie to the board GND plane. Design unchanged.

**🟢 2 — RESOLVED (module-confirmed) — Amplifier `GAIN`/`SD` defaults.**
J3.4 (GAIN) and J3.5 (SD) are left NC, relying on the breakout's onboard
resistors. The module's **back-side silkscreen** (now captured in
`images/max98357a-gain-sd-defaults.jpg` and documented in the Amplifier section)
explicitly states its as-shipped defaults: **"Default 9db Gain & (L+R)/2 out"**,
`MAX98357A I2S Mono Amp.`, `Vin: 2.5-5.5V`, `4-8Ω 3W`. This confirms the board
actively pulls `SD` to an *enabled* state in (L+R)/2 mono and leaves `GAIN`
floating for +9 dB — so leaving both pins unconnected on the carrier is correct
and the amp powers up enabled. **Residual check (assembly-time only):** confirm
the unit actually received is the pictured module and not a bare clone lacking
the `SD` pull; the 5 V VIN is within the printed 2.5–5.5 V range and the 4 Ω
speaker is within the printed 4–8 Ω range.

**🟢 3 — RESOLVED — Speaker wording inconsistency.**
The Speaker section previously said the speaker connects "via a 2-pin board
connector," contradicting the PCB Board section ("not a PCB connector"). The
schematic/PCB correctly have **no** speaker connector. **Fixed in `pcb.md`:** the
Speaker section now states the speaker wires directly to the amplifier module's
`OUT+`/`OUT-` terminals and is not a carrier-PCB connector. Design unchanged.

**🟢 4 — No action needed — No external I2C pull-ups / no 3V3 bulk cap.**
Acceptable: the Pi has fixed 1.8 kΩ pull-ups on BCM2/3, and the accessory
modules carry their own local decoupling. Noted for completeness.

## Remaining manufacturing gates (cannot be closed from CAD)

Concur with `PRE_MANUFACTURING_VALIDATION.md`. Load-bearing items:

- **Mate/orientation of J1 (2×20) and J2 (15-pin JST GH) cables** — verify pin-1
  and that neither can seat reversed.
- **Physical fit** of the exact INMP441 and MAX98357A modules over a 1:1
  printout.
- **C1 voltage rating** ≥ 6.3 V (10 V preferred); confirm polarity at assembly.
- **Supply budget** for amplifier peaks (~650 mA) to avoid Pi undervoltage.
- **Fab DFM** — map to the chosen vendor's 1.6 mm 4-layer stack (no controlled
  impedance required).
- First-article **continuity / rail-short / functional** bring-up.

## Verdict

**The electrical design is sound and internally consistent — netlist, ERC, DRC,
and schematic↔PCB parity all pass independent verification, and the
I2S/backlight pin-conflict resolution (the trickiest part) is correct.** All
three review findings are now closed: the two documentation discrepancies
(#1, #3) were corrected in `pcb.md`, and the amplifier default-config
uncertainty (#2) is resolved by the module's own silkscreen, which documents
9 dB gain and (L+R)/2 enabled mono output with `GAIN`/`SD` unconnected. The
board files were already correct and were not changed. The design is suitable
for prototype fabrication; only the physical mating/fit gates above (cable
orientation, module footprints, C1 rating, supply budget, fab DFM, first-article
bring-up) remain — none of which can be closed from CAD files alone.
