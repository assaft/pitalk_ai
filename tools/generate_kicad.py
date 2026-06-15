#!/usr/bin/env python3
"""Generate KiCad 7 project files for PiTalk PCB (rev 2.0).

GPIO assignments (Raspberry Pi Zero 2W):
  Pin 1/17  3.3V       → +3V3
  Pin 2/4   5V         → +5V
  Pin 3     GPIO2 SDA  → I2C_SDA  (touch screen)
  Pin 5     GPIO3 SCL  → I2C_SCL  (touch screen)
  Pin 7     GPIO4      → TOUCH_INT
  Pin 12    GPIO18     → I2S_BCLK (amp BCLK + mic SCK)
  Pin 13    GPIO27     → DISP_RST
  Pin 15    GPIO22     → BTN_SW
  Pin 19    GPIO10     → SPI_MOSI (screen)
  Pin 22    GPIO25     → DISP_DC
  Pin 23    GPIO11     → SPI_SCLK (screen)
  Pin 24    GPIO8      → SPI_CE0  (screen)
  Pin 32    GPIO12     → DISP_BL  (backlight PWM)
  Pin 33    GPIO13     → GPIO13   (→ R1 → BTN_LED)
  Pin 35    GPIO19     → I2S_LRCLK (amp LRC + mic WS)
  Pin 38    GPIO20     → I2S_DIN  (mic SD → RPi)
  Pin 40    GPIO21     → I2S_DOUT (RPi → amp DIN)
  GND: pins 6,9,14,20,25,30,34,39
"""
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB_DIR = ROOT / "pcb"
PCB_DIR.mkdir(exist_ok=True)


def uid() -> str:
    return str(uuid.uuid4())


# ── Net table ────────────────────────────────────────────────────────────────
NETS: list[tuple[int, str]] = [
    (0,  ""),
    (1,  "GND"),
    (2,  "+3V3"),
    (3,  "+5V"),
    (4,  "SPI_MOSI"),
    (5,  "SPI_SCLK"),
    (6,  "SPI_CE0"),
    (7,  "DISP_DC"),
    (8,  "DISP_RST"),
    (9,  "DISP_BL"),
    (10, "I2C_SDA"),
    (11, "I2C_SCL"),
    (12, "TOUCH_INT"),
    (13, "I2S_BCLK"),
    (14, "I2S_LRCLK"),
    (15, "I2S_DIN"),
    (16, "I2S_DOUT"),
    (17, "BTN_SW"),
    (18, "GPIO13"),
    (19, "BTN_LED"),
]
NETNAME = {n: name for n, name in NETS}

GND  = 1
V3V3 = 2
V5V  = 3

# J1: RPi 40-pin header — pad number → net id
J1_MAP = {
    1: V3V3, 2: V5V,
    3: 10,   4: V5V,
    5: 11,   6: GND,
    7: 12,   8: 0,
    9: GND,  10: 0,
    11: 0,   12: 13,
    13: 8,   14: GND,
    15: 17,  16: 0,
    17: V3V3,18: 0,
    19: 4,   20: GND,
    21: 0,   22: 7,
    23: 5,   24: 6,
    25: GND, 26: 0,
    27: 0,   28: 0,
    29: 0,   30: GND,
    31: 0,   32: 9,
    33: 18,  34: GND,
    35: 14,  36: 0,
    37: 0,   38: 15,
    39: GND, 40: 16,
}

# J2: Molex KK-254 1×15 (screen)
J2_MAP = {
    1: GND,  2: V3V3, 3: GND,  4: V3V3,
    5: 4,    6: 5,    7: 6,    8: 7,
    9: 8,    10: 10,  11: 11,  12: 12,
    13: 9,   14: GND, 15: V3V3,
}

# J3: PinHeader 2×3 (mic INMP441)
#   Pad layout: col0(x=0)=VDD,GND,L/R  col1(x=2.54)=SCK,WS,SD
J3_MAP = {1: V3V3, 2: 13, 3: GND, 4: 14, 5: GND, 6: 15}

# J4: PinSocket 1×7 (MAX98357 amp — female socket)
#   SD_MODE→+3V3 (always enabled), GAIN→GND (9 dB)
J4_MAP = {1: V5V, 2: GND, 3: V3V3, 4: GND, 5: 16, 6: 13, 7: 14}

# J5: PinHeader 1×4 (button + LED)
J5_MAP = {1: 17, 2: GND, 3: 19, 4: GND}

# R1: 330 Ω 0402 (BTN_LED current limiter)
R1_MAP = {1: 18, 2: 19}

# C1: 100 nF 0402 (+3V3 decoupling)
C1_MAP = {1: V3V3, 2: GND}

# C2: 100 nF 0402 (+5V decoupling)
C2_MAP = {1: V5V, 2: GND}


# ── PCB low-level helpers ────────────────────────────────────────────────────

def _net(net_id: int) -> str:
    if net_id == 0:
        return ""
    return f'\n\t\t\t(net {net_id} "{NETNAME[net_id]}")'


def tht_pad(num, x, y, net_id=0, size=(1.7, 1.7), drill=1.0, first=False):
    shape = "roundrect" if first else "circle"
    rratio = '\n\t\t\t(roundrect_rratio 0.25)' if first else ""
    return (
        f'\n\t\t(pad "{num}" thru_hole {shape}'
        f'\n\t\t\t(at {x:.3f} {y:.3f})'
        f'\n\t\t\t(size {size[0]} {size[1]})'
        f'\n\t\t\t(drill {drill}){rratio}'
        f'\n\t\t\t(layers "*.Cu" "*.Mask")'
        f'\n\t\t\t(remove_unused_layers no){_net(net_id)}'
        f'\n\t\t\t(uuid "{uid()}")'
        f'\n\t\t)'
    )


def smd_pad(num, x, y, net_id=0, size=(0.54, 0.64)):
    return (
        f'\n\t\t(pad "{num}" smd roundrect'
        f'\n\t\t\t(at {x:.4f} {y:.4f})'
        f'\n\t\t\t(size {size[0]} {size[1]})'
        f'\n\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")'
        f'\n\t\t\t(roundrect_rratio 0.25){_net(net_id)}'
        f'\n\t\t\t(uuid "{uid()}")'
        f'\n\t\t)'
    )


def npth_pad(x, y, drill=3.2):
    return (
        f'\n\t\t(pad "" np_thru_hole circle'
        f'\n\t\t\t(at {x:.2f} {y:.2f})'
        f'\n\t\t\t(size {drill} {drill})'
        f'\n\t\t\t(drill {drill})'
        f'\n\t\t\t(layers "*.Cu" "*.Mask")'
        f'\n\t\t\t(uuid "{uid()}")'
        f'\n\t\t)'
    )


def silk_line(x1, y1, x2, y2, w=0.12):
    return (
        f'\n\t\t(fp_line'
        f'\n\t\t\t(start {x1:.3f} {y1:.3f})'
        f'\n\t\t\t(end {x2:.3f} {y2:.3f})'
        f'\n\t\t\t(stroke (width {w}) (type solid))'
        f'\n\t\t\t(layer "F.SilkS")'
        f'\n\t\t\t(uuid "{uid()}")'
        f'\n\t\t)'
    )


def crtyd_rect(x1, y1, x2, y2):
    return (
        f'\n\t\t(fp_rect'
        f'\n\t\t\t(start {x1:.3f} {y1:.3f})'
        f'\n\t\t\t(end {x2:.3f} {y2:.3f})'
        f'\n\t\t\t(stroke (width 0.05) (type solid))'
        f'\n\t\t\t(fill no)'
        f'\n\t\t\t(layer "F.CrtYd")'
        f'\n\t\t\t(uuid "{uid()}")'
        f'\n\t\t)'
    )


def fp_ref(ref, ax, ay, rot=0):
    return (
        f'\n\t\t(property "Reference" "{ref}"'
        f'\n\t\t\t(at {ax:.2f} {ay:.2f} {rot})'
        f'\n\t\t\t(layer "F.SilkS")'
        f'\n\t\t\t(effects (font (size 1 1) (thickness 0.15)))'
        f'\n\t\t)'
    )


def fp_val(val, ax, ay, rot=0):
    return (
        f'\n\t\t(property "Value" "{val}"'
        f'\n\t\t\t(at {ax:.2f} {ay:.2f} {rot})'
        f'\n\t\t\t(layer "F.Fab")'
        f'\n\t\t\t(effects (font (size 1 1) (thickness 0.15)))'
        f'\n\t\t)'
    )


def footprint_header(name, ref, val, at_x, at_y, at_rot, fp_uuid, layer="F.Cu"):
    rot_str = f" {at_rot}" if at_rot else ""
    return (
        f'\n(footprint "{name}"'
        f'\n\t(version 20260206)'
        f'\n\t(generator "pitalk-gen")'
        f'\n\t(layer "{layer}")'
        f'\n\t(uuid "{fp_uuid}")'
        f'\n\t(at {at_x:.3f} {at_y:.3f}{rot_str})'
        f'\n\t(attr through_hole)'
        f'\n\t(duplicate_pad_numbers_are_jumpers no)'
    )


def footprint_close(model_path=None):
    if model_path:
        return (
            f'\n\t(embedded_fonts no)'
            f'\n\t(model "{model_path}"'
            f'\n\t\t(offset (xyz 0 0 0))'
            f'\n\t\t(scale (xyz 1 1 1))'
            f'\n\t\t(rotate (xyz 0 0 0))'
            f'\n\t)'
            f'\n)'
        )
    return '\n\t(embedded_fonts no)\n)'


# ── PCB footprint builders ────────────────────────────────────────────────────

def build_idc_2x20(net_map):
    """IDC shrouded 2×20 male header for RPi connection."""
    fp_id = uid()
    s = footprint_header(
        "Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical",
        "J1", "RPi_GPIO_40pin_IDC",
        58.0, 47.0, 270, fp_id,
    )
    s += fp_ref("J1", 1.27, -6.1)
    s += fp_val("RPi_GPIO_40pin_IDC", 1.27, 54.36)
    # Body outline (local coords, before rotation)
    s += silk_line(-3.29, -5.21,  5.83, -5.21)
    s += silk_line( 5.83, -5.21,  5.83, 53.47)
    s += silk_line( 5.83, 53.47, -3.29, 53.47)
    s += silk_line(-3.29, 53.47, -3.29, -5.21)
    # Pin 1 indicator triangle
    s += silk_line(-4.68, -0.5, -3.68, 0.0)
    s += silk_line(-3.68,  0.0, -4.68, 0.5)
    s += silk_line(-4.68,  0.5, -4.68, -0.5)
    # Courtyard
    s += crtyd_rect(-3.68, -5.6, 6.22, 53.86)
    # Pads: pin n at local (col*2.54, row*2.54)
    # col = (n-1)%2, row = (n-1)//2
    for n in range(1, 41):
        col = (n - 1) % 2
        row = (n - 1) // 2
        x, y = col * 2.54, row * 2.54
        s += tht_pad(n, x, y, net_map.get(n, 0), first=(n == 1))
    s += footprint_close("${KICAD10_3DMODEL_DIR}/Connector_IDC.3dshapes/IDC-Header_2x20_P2.54mm_Vertical.step")
    return s


def build_molex_kk_1x15(net_map):
    """Molex KK-254 1×15 locking connector (screen)."""
    fp_id = uid()
    s = footprint_header(
        "Connector_Molex:Molex_KK-254_AE-6410-15A_1x15_P2.54mm_Vertical",
        "J2", "Screen_Waveshare_2in_Molex_KK_254",
        7.0, 6.0, 0, fp_id,
    )
    s += fp_ref("J2", 0, -3.5)
    s += fp_val("Screen_Waveshare_2in_Molex_KK_254", 0, 39.0)
    # Simple rectangular body outline
    total_len = 14 * 2.54
    s += silk_line(-1.67, -2.0, -1.67, total_len + 2.0)
    s += silk_line(-1.67, -2.0,  1.67, -2.0)
    s += silk_line( 1.67, -2.0,  1.67, total_len + 2.0)
    s += silk_line(-1.67, total_len + 2.0, 1.67, total_len + 2.0)
    s += crtyd_rect(-2.17, -2.5, 2.17, total_len + 2.5)
    for n in range(1, 16):
        y = (n - 1) * 2.54
        s += tht_pad(n, 0, y, net_map.get(n, 0), first=(n == 1))
    s += footprint_close()
    return s


def build_pinheader_2x03(net_map):
    """2×3 male pin header (mic INMP441)."""
    fp_id = uid()
    s = footprint_header(
        "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical",
        "J3", "Mic_INMP441_Male_Header",
        54.0, 6.0, 0, fp_id,
    )
    s += fp_ref("J3", 1.27, -2.5)
    s += fp_val("Mic_INMP441_Male_Header", 1.27, 8.0)
    s += silk_line(-1.33, -1.33, 3.87, -1.33)
    s += silk_line( 3.87, -1.33, 3.87, 6.87)
    s += silk_line( 3.87,  6.87, -1.33, 6.87)
    s += silk_line(-1.33,  6.87, -1.33, -1.33)
    s += crtyd_rect(-1.83, -1.83, 4.37, 7.37)
    # 2 cols × 3 rows; pad n: col=(n-1)%2, row=(n-1)//2
    for n in range(1, 7):
        col = (n - 1) % 2
        row = (n - 1) // 2
        s += tht_pad(n, col * 2.54, row * 2.54, net_map.get(n, 0), first=(n == 1))
    s += footprint_close()
    return s


def build_pinsocket_1x07(net_map):
    """1×7 female pin socket (MAX98357 amp)."""
    fp_id = uid()
    s = footprint_header(
        "Connector_PinSocket_2.54mm:PinSocket_1x07_P2.54mm_Vertical",
        "J4", "External_MAX98357A_Amp_Female",
        6.0, 21.0, 0, fp_id,
    )
    s += fp_ref("J4", 0, -2.77)
    s += fp_val("External_MAX98357A_Amp_Female", 0, 18.01)
    total = 6 * 2.54
    s += silk_line(-1.33, -1.33,  1.33, -1.33)
    s += silk_line( 1.33, -1.33,  1.33, total + 1.33)
    s += silk_line( 1.33, total + 1.33, -1.33, total + 1.33)
    s += silk_line(-1.33, total + 1.33, -1.33, -1.33)
    s += crtyd_rect(-1.83, -1.83, 1.83, total + 1.83)
    for n in range(1, 8):
        s += tht_pad(n, 0, (n - 1) * 2.54, net_map.get(n, 0),
                     size=(1.7, 1.7), drill=1.1, first=(n == 1))
    s += footprint_close()
    return s


def build_pinheader_1xN(ref, val, at_x, at_y, at_rot, n_pins, net_map):
    """Generic 1×N THT pin header."""
    fp_id = uid()
    s = footprint_header(
        f"Connector_PinHeader_2.54mm:PinHeader_1x{n_pins:02d}_P2.54mm_Vertical",
        ref, val, at_x, at_y, at_rot, fp_id,
    )
    total = (n_pins - 1) * 2.54
    s += fp_ref(ref, 0, -2.0)
    s += fp_val(val, 0, total + 2.0)
    s += silk_line(-1.33, -1.33, 1.33, -1.33)
    s += silk_line( 1.33, -1.33, 1.33, total + 1.33)
    s += silk_line( 1.33, total + 1.33, -1.33, total + 1.33)
    s += silk_line(-1.33, total + 1.33, -1.33, -1.33)
    s += crtyd_rect(-1.83, -1.83, 1.83, total + 1.83)
    for n in range(1, n_pins + 1):
        s += tht_pad(n, 0, (n - 1) * 2.54, net_map.get(n, 0), first=(n == 1))
    s += footprint_close()
    return s


def build_r0402(ref, val, at_x, at_y, net_map):
    """SMD 0402 resistor or capacitor."""
    fp_id = uid()
    s = footprint_header(
        "Resistor_SMD:R_0402_1005Metric",
        ref, val, at_x, at_y, 0, fp_id, layer="F.Cu",
    )
    s = s.replace("(attr through_hole)", "(attr smd)")
    s += fp_ref(ref, 0, -1.17)
    s += fp_val(val, 0, 1.17)
    s += silk_line(-0.154, -0.38, 0.154, -0.38)
    s += silk_line(-0.154,  0.38, 0.154,  0.38)
    s += crtyd_rect(-0.93, -0.47, 0.93, 0.47)
    s += smd_pad(1, -0.51, 0, net_map.get(1, 0))
    s += smd_pad(2,  0.51, 0, net_map.get(2, 0))
    s += footprint_close()
    return s


def build_c0402(ref, val, at_x, at_y, net_map):
    """SMD 0402 capacitor (same footprint as resistor)."""
    s = build_r0402(ref, val, at_x, at_y, net_map)
    return s.replace("Resistor_SMD:R_0402_1005Metric",
                     "Capacitor_SMD:C_0402_1005Metric")


def build_mounting_hole(ref, at_x, at_y):
    """M3 non-plated mounting hole."""
    fp_id = uid()
    s = footprint_header(
        "MountingHole:MountingHole_3.2mm_M3",
        ref, "M3", at_x, at_y, 0, fp_id,
    )
    s = s.replace("(attr through_hole)", "(attr exclude_from_bom exclude_from_pos_files)")
    s += fp_ref(ref, 0, -3.0)
    s += npth_pad(0, 0, 3.2)
    s += crtyd_rect(-2.5, -2.5, 2.5, 2.5)
    s += '\n\t(embedded_fonts no)\n)'
    return s


# ── PCB file ─────────────────────────────────────────────────────────────────

def generate_pcb() -> str:
    net_decls = "\n".join(f'\t(net {n} "{name}")' for n, name in NETS)

    # Board outline 65×55 mm
    board_uuid = uid()

    parts = [
        f"""(kicad_pcb
\t(version 20241229)
\t(generator "pitalk-gen")
\t(generator_version "2.0")
\t(general (thickness 1.6) (legacy_teardrops no))
\t(paper "A4")
\t(title_block (title "PiTalk PCB") (date "2026-06-07") (rev "2.0") (company "PiTalk"))
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(25 "Edge.Cuts" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t)
{net_decls}
\t(gr_rect (start 0 0) (end 65 55)
\t\t(stroke (width 0.1) (type solid)) (fill no)
\t\t(layer "Edge.Cuts") (uuid "{board_uuid}"))""",
    ]

    # Silkscreen component labels
    labels = [
        ("J1 GPIO IDC (to RPi)", 29.0, 52.5),
        ("J2 SCREEN (locking)", 9.5, 3.5),
        ("J3 MIC (male hdr)", 53.0, 3.5),
        ("J4 AMP (female sckt)", 8.5, 18.5),
        ("J5 BTN", 7.0, 34.5),
        ("R1 330R BTN_LED", 23.0, 36.5),
        ("C1 100nF +3V3", 37.5, 36.5),
        ("C2 100nF +5V", 42.5, 36.5),
    ]
    for text, lx, ly in labels:
        parts.append(
            f'\t(gr_text "{text}" (at {lx} {ly} 0) (layer "F.SilkS")'
            f' (uuid "{uid()}")'
            f' (effects (font (size 1 1) (thickness 0.15))))'
        )

    # Footprints
    parts.append(build_idc_2x20(J1_MAP))
    parts.append(build_molex_kk_1x15(J2_MAP))
    parts.append(build_pinheader_2x03(J3_MAP))
    parts.append(build_pinsocket_1x07(J4_MAP))
    parts.append(build_pinheader_1xN("J5", "Button_LED", 15.0, 37.0, 90, 4, J5_MAP))
    parts.append(build_r0402("R1", "330R", 25.0, 39.0, R1_MAP))
    parts.append(build_c0402("C1", "100nF", 40.0, 39.0, C1_MAP))
    parts.append(build_c0402("C2", "100nF", 45.0, 39.0, C2_MAP))
    # Mounting holes
    for mh_ref, mx, my in [("MH1", 3.2, 3.2), ("MH2", 61.8, 3.2),
                            ("MH3", 3.2, 51.8), ("MH4", 61.8, 51.8)]:
        parts.append(build_mounting_hole(mh_ref, mx, my))

    parts.append(")")
    return "\n".join(parts)


# ── Schematic helpers ─────────────────────────────────────────────────────────

def glabel(x, y, value, shape="bidirectional", rot=0):
    """Global net label."""
    j = "left" if rot == 0 else "right"
    dx = 6 if rot == 0 else -6
    return (
        f'  (global_label (at {x} {y} {rot}) (shape {shape}) (fields_autoplaced yes)\n'
        f'    (effects (font (size 1.27 1.27)) (justify {j}))\n'
        f'    (property "Value" "{value}" (id 0) (at {x+dx} {y} {rot})\n'
        f'      (effects (font (size 1.27 1.27)) (justify {j}))\n'
        f'    )\n'
        f'    (pin (at {x} {y} {180 if rot == 0 else 0}) (length 2.54))\n'
        f'    (uuid "{uid()}")\n'
        f'  )\n'
    )


def pwr_sym(x, y, net_name, rot=0):
    """Power flag symbol (+3V3, +5V, GND)."""
    return (
        f'  (symbol (lib_id "power:{net_name}") (at {x} {y} {rot}) (unit 1)\n'
        f'    (in_bom yes) (on_board yes)\n'
        f'    (uuid "{uid()}")\n'
        f'    (property "Reference" "#PWR" (id 0) (at {x} {y+2.5} {rot})\n'
        f'      (effects (font (size 1.27 1.27)) hide)\n'
        f'    )\n'
        f'    (property "Value" "{net_name}" (id 1) (at {x} {y-2.5} {rot})\n'
        f'      (effects (font (size 1.27 1.27)))\n'
        f'    )\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'  )\n'
    )


def noconn(x, y):
    return f'  (no_connect (at {x} {y}) (uuid "{uid()}"))\n'


def sym_inst(lib_id, ref, val, fp, at_x, at_y, at_rot=0, extra_props=None):
    """Generic symbol instance."""
    lines = [
        f'  (symbol (lib_id "{lib_id}") (at {at_x} {at_y} {at_rot}) (unit 1)\n',
        f'    (in_bom yes) (on_board yes)\n',
        f'    (uuid "{uid()}")\n',
        f'    (property "Reference" "{ref}" (id 0) (at {at_x} {at_y - 5} 0)\n',
        f'      (effects (font (size 1.27 1.27)))\n',
        f'    )\n',
        f'    (property "Value" "{val}" (id 1) (at {at_x} {at_y + 5} 0)\n',
        f'      (effects (font (size 1.27 1.27)))\n',
        f'    )\n',
        f'    (property "Footprint" "{fp}" (id 2) (at {at_x} {at_y} 0)\n',
        f'      (effects (font (size 1.27 1.27)) hide)\n',
        f'    )\n',
    ]
    if extra_props:
        lines += extra_props
    lines.append(f'  )\n')
    return "".join(lines)


# ── Schematic symbol library (inline) ────────────────────────────────────────

SCHEMATIC_LIB = r"""
  (lib_symbols

    ;; RPi GPIO 2×20 IDC shrouded male header
    (symbol "Conn_02x20_Odd_Even"
      (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (id 0) (at 0 53.34 0) (effects (font (size 1.27 1.27))))
      (property "Value" "RPi_GPIO_40pin_IDC" (id 1) (at 0 -53.34 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_02x20_Odd_Even_1_1"
        (rectangle (start -1.27 52.705) (end 3.81 -52.705)
          (stroke (width 0) (type default)) (fill (type pin_numbers_background)))
        ;; — odd pins (left column, GPIO signals) —
        (pin passive (at -5.08  50.80 0) (length 3.81) (name "3V3"      (effects (font (size 1.27 1.27)))) (number "1"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  45.72 0) (length 3.81) (name "I2C_SDA"  (effects (font (size 1.27 1.27)))) (number "3"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  40.64 0) (length 3.81) (name "I2C_SCL"  (effects (font (size 1.27 1.27)))) (number "5"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  35.56 0) (length 3.81) (name "TOUCH_INT" (effects (font (size 1.27 1.27)))) (number "7"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  30.48 0) (length 3.81) (name "GND"      (effects (font (size 1.27 1.27)))) (number "9"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  25.40 0) (length 3.81) (name "NC"       (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  20.32 0) (length 3.81) (name "DISP_RST" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  15.24 0) (length 3.81) (name "BTN_SW"   (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  10.16 0) (length 3.81) (name "3V3"      (effects (font (size 1.27 1.27)))) (number "17" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08   5.08 0) (length 3.81) (name "SPI_MOSI" (effects (font (size 1.27 1.27)))) (number "19" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08   0.00 0) (length 3.81) (name "NC"       (effects (font (size 1.27 1.27)))) (number "21" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  -5.08 0) (length 3.81) (name "SPI_SCLK" (effects (font (size 1.27 1.27)))) (number "23" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -10.16 0) (length 3.81) (name "GND"      (effects (font (size 1.27 1.27)))) (number "25" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -15.24 0) (length 3.81) (name "NC"       (effects (font (size 1.27 1.27)))) (number "27" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -20.32 0) (length 3.81) (name "NC"       (effects (font (size 1.27 1.27)))) (number "29" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -25.40 0) (length 3.81) (name "NC"       (effects (font (size 1.27 1.27)))) (number "31" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -30.48 0) (length 3.81) (name "BTN_LED"  (effects (font (size 1.27 1.27)))) (number "33" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -35.56 0) (length 3.81) (name "I2S_LRCLK"(effects (font (size 1.27 1.27)))) (number "35" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -40.64 0) (length 3.81) (name "NC"       (effects (font (size 1.27 1.27)))) (number "37" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -45.72 0) (length 3.81) (name "GND"      (effects (font (size 1.27 1.27)))) (number "39" (effects (font (size 1.27 1.27)))))
        ;; — even pins (right column, power + audio) —
        (pin passive (at  8.89  50.80 180) (length 3.81) (name "+5V"       (effects (font (size 1.27 1.27)))) (number "2"  (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  45.72 180) (length 3.81) (name "+5V"       (effects (font (size 1.27 1.27)))) (number "4"  (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  40.64 180) (length 3.81) (name "GND"       (effects (font (size 1.27 1.27)))) (number "6"  (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  35.56 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "8"  (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  30.48 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  25.40 180) (length 3.81) (name "I2S_BCLK" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  20.32 180) (length 3.81) (name "GND"       (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  15.24 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  10.16 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "18" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89   5.08 180) (length 3.81) (name "GND"       (effects (font (size 1.27 1.27)))) (number "20" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89   0.00 180) (length 3.81) (name "DISP_DC"   (effects (font (size 1.27 1.27)))) (number "22" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89  -5.08 180) (length 3.81) (name "SPI_CE0"   (effects (font (size 1.27 1.27)))) (number "24" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -10.16 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "26" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -15.24 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "28" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -20.32 180) (length 3.81) (name "GND"       (effects (font (size 1.27 1.27)))) (number "30" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -25.40 180) (length 3.81) (name "DISP_BL"   (effects (font (size 1.27 1.27)))) (number "32" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -30.48 180) (length 3.81) (name "GND"       (effects (font (size 1.27 1.27)))) (number "34" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -35.56 180) (length 3.81) (name "NC"        (effects (font (size 1.27 1.27)))) (number "36" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -40.64 180) (length 3.81) (name "I2S_DIN"   (effects (font (size 1.27 1.27)))) (number "38" (effects (font (size 1.27 1.27)))))
        (pin passive (at  8.89 -45.72 180) (length 3.81) (name "I2S_DOUT"  (effects (font (size 1.27 1.27)))) (number "40" (effects (font (size 1.27 1.27)))))
      )
    )

    ;; 1×15 keyed locking connector (Screen — Waveshare 2", Molex KK-254)
    (symbol "Conn_01x15_Screen"
      (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (id 0) (at 0 20.32 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Screen_Waveshare_2in" (id 1) (at 0 -20.32 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_Molex:Molex_KK-254_AE-6410-15A_1x15_P2.54mm_Vertical" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_01x15_Screen_1_1"
        (rectangle (start -1.27 19.685) (end 1.27 -19.685)
          (stroke (width 0) (type default)) (fill (type pin_numbers_background)))
        (pin passive (at -5.08  17.78 0) (length 3.81) (name "GND"   (effects (font (size 1.27 1.27)))) (number "1"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  15.24 0) (length 3.81) (name "+3V3"  (effects (font (size 1.27 1.27)))) (number "2"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  12.70 0) (length 3.81) (name "GND"   (effects (font (size 1.27 1.27)))) (number "3"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  10.16 0) (length 3.81) (name "+3V3"  (effects (font (size 1.27 1.27)))) (number "4"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08   7.62 0) (length 3.81) (name "MOSI"  (effects (font (size 1.27 1.27)))) (number "5"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08   5.08 0) (length 3.81) (name "SCLK"  (effects (font (size 1.27 1.27)))) (number "6"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08   2.54 0) (length 3.81) (name "CS"    (effects (font (size 1.27 1.27)))) (number "7"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08   0.00 0) (length 3.81) (name "DC"    (effects (font (size 1.27 1.27)))) (number "8"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  -2.54 0) (length 3.81) (name "RST"   (effects (font (size 1.27 1.27)))) (number "9"  (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  -5.08 0) (length 3.81) (name "SDA"   (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  -7.62 0) (length 3.81) (name "SCL"   (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -10.16 0) (length 3.81) (name "INT"   (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -12.70 0) (length 3.81) (name "BL"    (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -15.24 0) (length 3.81) (name "GND"   (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -17.78 0) (length 3.81) (name "+3V3"  (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))
      )
    )

    ;; 2×3 male header (microphone INMP441)
    (symbol "Conn_02x03_Mic"
      (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (id 0) (at 0 6.35 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Mic_INMP441" (id 1) (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_02x03_Mic_1_1"
        (rectangle (start -1.27 5.715) (end 1.27 -5.715)
          (stroke (width 0) (type default)) (fill (type pin_numbers_background)))
        (pin passive (at -5.08  3.81 0) (length 3.81) (name "VDD" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  1.27 0) (length 3.81) (name "GND" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -1.27 0) (length 3.81) (name "L/R" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin passive (at  5.08  3.81 180) (length 3.81) (name "SCK" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive (at  5.08  1.27 180) (length 3.81) (name "WS"  (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin passive (at  5.08 -1.27 180) (length 3.81) (name "SD"  (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
      )
    )

    ;; 1×7 female socket (external MAX98357A amplifier)
    (symbol "Conn_01x07_Amp"
      (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (id 0) (at 0 10.16 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Amp_MAX98357A" (id 1) (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinSocket_2.54mm:PinSocket_1x07_P2.54mm_Vertical" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_01x07_Amp_1_1"
        (rectangle (start -1.27 9.525) (end 1.27 -9.525)
          (stroke (width 0) (type default)) (fill (type pin_numbers_background)))
        (pin passive (at -5.08  7.62 0) (length 3.81) (name "VIN"     (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  5.08 0) (length 3.81) (name "GND"     (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  2.54 0) (length 3.81) (name "SD_MODE" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  0.00 0) (length 3.81) (name "GAIN"    (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -2.54 0) (length 3.81) (name "DIN"     (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -5.08 0) (length 3.81) (name "BCLK"   (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -7.62 0) (length 3.81) (name "LRC"    (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
      )
    )

    ;; 1×4 connector (button + LED)
    (symbol "Conn_01x04_Button"
      (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (id 0) (at 0 6.35 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Button_LED" (id 1) (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_01x04_Button_1_1"
        (rectangle (start -1.27 5.715) (end 1.27 -5.715)
          (stroke (width 0) (type default)) (fill (type pin_numbers_background)))
        (pin passive (at -5.08  3.81 0) (length 3.81) (name "BTN_SW"  (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08  1.27 0) (length 3.81) (name "GND"     (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -1.27 0) (length 3.81) (name "BTN_LED" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin passive (at -5.08 -3.81 0) (length 3.81) (name "GND"     (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
      )
    )

    ;; 1×2 connector (speaker output)
    ;; Resistor
    (symbol "R"
      (in_bom yes) (on_board yes)
      (property "Reference" "R" (id 0) (at 1.524 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (id 1) (at -1.524 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_1_1"
        (rectangle (start -1.016 -2.667) (end 1.016 2.667)
          (stroke (width 0) (type default)) (fill (type none)))
        (pin passive (at 0  3.81 270) (length 1.143) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive (at 0 -3.81  90) (length 1.143) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )

    ;; Capacitor
    (symbol "C"
      (in_bom yes) (on_board yes)
      (property "Reference" "C" (id 0) (at 1.524 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (id 1) (at -1.524 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_1_1"
        (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762))
          (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy -2.032  0.762) (xy 2.032  0.762))
          (stroke (width 0.508) (type default)) (fill (type none)))
        (pin passive (at 0  1.905 270) (length 1.143) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive (at 0 -1.905  90) (length 1.143) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )

  ) ;; end lib_symbols
"""


# ── Schematic file ────────────────────────────────────────────────────────────

def generate_sch() -> str:
    parts = [
        f"""(kicad_sch
  (version 20230121)
  (generator "pitalk-gen")
  (paper "A2")
  (title_block
    (title "PiTalk PCB Schematic")
    (date "2026-06-07")
    (rev "2.0")
    (company "PiTalk")
    (comment 1 "Voice messaging device for kids — Raspberry Pi Zero 2W")
    (comment 2 "Connectors: screen (locking), mic, amp (ext), speaker, button")
  )
  (uuid "{uid()}")
""",
        SCHEMATIC_LIB,
    ]

    # ── J1 RPi header ────────────────────────────────────────────────
    #  Placed at (35, 80).  Left-col endpoint x = 35 - 5.08 = 29.92
    #  Right-col endpoint x = 35 + 8.89 = 43.89
    #  Pin 1 y_abs = 80 - 50.80 = 29.20  …  Pin 39 y_abs = 80 + 45.72 = 125.72
    parts.append(
        f"""  ;; ── J1 — Raspberry Pi 40-pin IDC header ──────────────────────────
  (symbol (lib_id "Conn_02x20_Odd_Even") (at 35 80 0) (unit 1)
    (in_bom yes) (on_board yes)
    (uuid "{uid()}")
    (property "Reference" "J1" (id 0) (at 35 25 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "RPi_GPIO_40pin_IDC" (id 1) (at 35 137 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical" (id 2) (at 35 80 0)
      (effects (font (size 1.27 1.27)) hide))
  )
"""
    )

    # Left-column global labels & power symbols (x=29.92)
    lx = 29.92
    LEFT_PINS = [
        (50.80, "+3V3",     "power",       "pwr_sym"),
        (45.72, "I2C_SDA",  "bidirectional", "glabel"),
        (40.64, "I2C_SCL",  "bidirectional", "glabel"),
        (35.56, "TOUCH_INT","input",        "glabel"),
        (30.48, "GND",      "power",       "pwr_sym"),
        (25.40, None,       None,          "noconn"),   # pin 11 NC
        (20.32, "DISP_RST", "output",      "glabel"),
        (15.24, "BTN_SW",   "input",       "glabel"),
        (10.16, "+3V3",     "power",       "pwr_sym"),
        ( 5.08, "SPI_MOSI", "output",      "glabel"),
        ( 0.00, None,       None,          "noconn"),   # pin 21 NC
        (-5.08, "SPI_SCLK", "output",      "glabel"),
        (-10.16,"GND",      "power",       "pwr_sym"),
        (-15.24, None,      None,          "noconn"),   # pin 27 NC
        (-20.32, None,      None,          "noconn"),   # pin 29 NC
        (-25.40, None,      None,          "noconn"),   # pin 31 NC
        (-30.48, "GPIO13",  "output",      "glabel"),
        (-35.56, "I2S_LRCLK","bidirectional","glabel"),
        (-40.64, None,      None,          "noconn"),   # pin 37 NC
        (-45.72, "GND",     "power",       "pwr_sym"),
    ]
    for y_rel, name, shape, kind in LEFT_PINS:
        y_abs = 80 - y_rel
        if kind == "noconn":
            parts.append(noconn(lx, y_abs))
        elif kind == "pwr_sym":
            parts.append(pwr_sym(lx, y_abs, name, rot=180))
        elif kind == "glabel":
            parts.append(glabel(lx, y_abs, name, shape, rot=180))

    # Right-column global labels & power symbols (x=43.89)
    rx = 43.89
    RIGHT_PINS = [
        (50.80, "+5V",       "power",       "pwr_sym"),
        (45.72, "+5V",       "power",       "pwr_sym"),
        (40.64, "GND",       "power",       "pwr_sym"),
        (35.56, None,        None,          "noconn"),
        (30.48, None,        None,          "noconn"),
        (25.40, "I2S_BCLK",  "bidirectional","glabel"),
        (20.32, "GND",       "power",       "pwr_sym"),
        (15.24, None,        None,          "noconn"),
        (10.16, None,        None,          "noconn"),
        ( 5.08, "GND",       "power",       "pwr_sym"),
        ( 0.00, "DISP_DC",   "output",      "glabel"),
        (-5.08, "SPI_CE0",   "output",      "glabel"),
        (-10.16, None,       None,          "noconn"),
        (-15.24, None,       None,          "noconn"),
        (-20.32, "GND",      "power",       "pwr_sym"),
        (-25.40, "DISP_BL",  "output",      "glabel"),
        (-30.48, "GND",      "power",       "pwr_sym"),
        (-35.56, None,       None,          "noconn"),
        (-40.64, "I2S_DIN",  "input",       "glabel"),
        (-45.72, "I2S_DOUT", "output",      "glabel"),
    ]
    for y_rel, name, shape, kind in RIGHT_PINS:
        y_abs = 80 - y_rel
        if kind == "noconn":
            parts.append(noconn(rx, y_abs))
        elif kind == "pwr_sym":
            parts.append(pwr_sym(rx, y_abs, name))
        elif kind == "glabel":
            parts.append(glabel(rx, y_abs, name, shape))

    # ── J2 Screen connector ───────────────────────────────────────────
    j2x = 200
    j2y = 40
    parts.append(f"""  ;; ── J2 — Screen locking connector (Molex KK-254 1×15) ────────────
  (symbol (lib_id "Conn_01x15_Screen") (at {j2x} {j2y} 0) (unit 1)
    (in_bom yes) (on_board yes) (uuid "{uid()}")
    (property "Reference" "J2" (id 0) (at {j2x} {j2y-22} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Screen_Waveshare_2in" (id 1) (at {j2x} {j2y+22} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_Molex:Molex_KK-254_AE-6410-15A_1x15_P2.54mm_Vertical" (id 2) (at {j2x} {j2y} 0) (effects (font (size 1.27 1.27)) hide))
  )
""")
    # Pin endpoints: x = j2x - 5.08 = 194.92
    j2px = j2x - 5.08
    J2_LABELS = [
        ( 17.78, "GND",      "power",        "pwr_sym"),
        ( 15.24, "+3V3",     "power",        "pwr_sym"),
        ( 12.70, "GND",      "power",        "pwr_sym"),
        ( 10.16, "+3V3",     "power",        "pwr_sym"),
        (  7.62, "SPI_MOSI", "bidirectional","glabel"),
        (  5.08, "SPI_SCLK", "bidirectional","glabel"),
        (  2.54, "SPI_CE0",  "bidirectional","glabel"),
        (  0.00, "DISP_DC",  "bidirectional","glabel"),
        ( -2.54, "DISP_RST", "bidirectional","glabel"),
        ( -5.08, "I2C_SDA",  "bidirectional","glabel"),
        ( -7.62, "I2C_SCL",  "bidirectional","glabel"),
        (-10.16, "TOUCH_INT","bidirectional","glabel"),
        (-12.70, "DISP_BL",  "bidirectional","glabel"),
        (-15.24, "GND",      "power",        "pwr_sym"),
        (-17.78, "+3V3",     "power",        "pwr_sym"),
    ]
    for y_rel, name, shape, kind in J2_LABELS:
        y_abs = j2y - y_rel
        if kind == "pwr_sym":
            parts.append(pwr_sym(j2px, y_abs, name, rot=180))
        else:
            parts.append(glabel(j2px, y_abs, name, shape, rot=180))

    # ── J3 Mic connector ─────────────────────────────────────────────
    j3x, j3y = 200, 100
    parts.append(f"""  ;; ── J3 — Microphone connector (2×3 male header) ──────────────────
  (symbol (lib_id "Conn_02x03_Mic") (at {j3x} {j3y} 0) (unit 1)
    (in_bom yes) (on_board yes) (uuid "{uid()}")
    (property "Reference" "J3" (id 0) (at {j3x} {j3y-8} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Mic_INMP441" (id 1) (at {j3x} {j3y+8} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical" (id 2) (at {j3x} {j3y} 0) (effects (font (size 1.27 1.27)) hide))
  )
""")
    j3lx = j3x - 5.08   # left col endpoint
    j3rx = j3x + 5.08   # right col endpoint
    for y_rel, name, shape, kind, is_right in [
        (3.81, "+3V3",     "power",        "pwr_sym", False),
        (1.27, "GND",      "power",        "pwr_sym", False),
        (-1.27, "GND",     "power",        "pwr_sym", False),   # L/R → GND
        (3.81, "I2S_BCLK", "bidirectional","glabel",  True),
        (1.27, "I2S_LRCLK","bidirectional","glabel",  True),
        (-1.27,"I2S_DIN",  "bidirectional","glabel",  True),
    ]:
        y_abs = j3y - y_rel
        px = j3rx if is_right else j3lx
        rot = 0 if is_right else 180
        if kind == "pwr_sym":
            parts.append(pwr_sym(px, y_abs, name, rot=rot))
        else:
            parts.append(glabel(px, y_abs, name, shape, rot=rot))

    # ── J4 Amp socket ─────────────────────────────────────────────────
    j4x, j4y = 200, 130
    parts.append(f"""  ;; ── J4 — Amplifier socket (1×7 female, MAX98357A) ────────────────
  (symbol (lib_id "Conn_01x07_Amp") (at {j4x} {j4y} 0) (unit 1)
    (in_bom yes) (on_board yes) (uuid "{uid()}")
    (property "Reference" "J4" (id 0) (at {j4x} {j4y-12} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Amp_MAX98357A" (id 1) (at {j4x} {j4y+12} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_PinSocket_2.54mm:PinSocket_1x07_P2.54mm_Vertical" (id 2) (at {j4x} {j4y} 0) (effects (font (size 1.27 1.27)) hide))
  )
""")
    j4px = j4x - 5.08
    J4_LABELS = [
        (7.62, "+5V",       "power",        "pwr_sym"),
        (5.08, "GND",       "power",        "pwr_sym"),
        (2.54, "+3V3",      "power",        "pwr_sym"),  # SD_MODE held high
        (0.00, "GND",       "power",        "pwr_sym"),  # GAIN → GND (9 dB)
        (-2.54,"I2S_DOUT",  "bidirectional","glabel"),
        (-5.08,"I2S_BCLK",  "bidirectional","glabel"),
        (-7.62,"I2S_LRCLK", "bidirectional","glabel"),
    ]
    for y_rel, name, shape, kind in J4_LABELS:
        y_abs = j4y - y_rel
        if kind == "pwr_sym":
            parts.append(pwr_sym(j4px, y_abs, name, rot=180))
        else:
            parts.append(glabel(j4px, y_abs, name, shape, rot=180))

    # ── J5 Button connector ───────────────────────────────────────────
    j5x, j5y = 200, 165
    parts.append(f"""  ;; ── J5 — Button + LED connector (1×4 male) ─────────────────────
  (symbol (lib_id "Conn_01x04_Button") (at {j5x} {j5y} 0) (unit 1)
    (in_bom yes) (on_board yes) (uuid "{uid()}")
    (property "Reference" "J5" (id 0) (at {j5x} {j5y-8} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Button_LED" (id 1) (at {j5x} {j5y+8} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" (id 2) (at {j5x} {j5y} 0) (effects (font (size 1.27 1.27)) hide))
  )
""")
    j5px = j5x - 5.08
    for y_rel, name, shape, kind in [
        (3.81, "BTN_SW",  "bidirectional","glabel"),
        (1.27, "GND",     "power",        "pwr_sym"),
        (-1.27,"BTN_LED", "bidirectional","glabel"),
        (-3.81,"GND",     "power",        "pwr_sym"),
    ]:
        y_abs = j5y - y_rel
        if kind == "pwr_sym":
            parts.append(pwr_sym(j5px, y_abs, name, rot=180))
        else:
            parts.append(glabel(j5px, y_abs, name, shape, rot=180))

    # ── R1 — 330 Ω LED resistor ───────────────────────────────────────
    r1x, r1y = 120, 130
    parts.append(f"""  ;; ── R1 — 330 Ω BTN_LED current limiter ──────────────────────────
  (symbol (lib_id "R") (at {r1x} {r1y} 0) (unit 1)
    (in_bom yes) (on_board yes) (uuid "{uid()}")
    (property "Reference" "R1" (id 0) (at {r1x+2} {r1y} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "330R" (id 1) (at {r1x-2} {r1y} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_SMD:R_0402_1005Metric" (id 2) (at {r1x} {r1y} 0) (effects (font (size 1.27 1.27)) hide))
  )
""")
    # R1 pin 1 at (r1x, r1y-3.81)  pin 2 at (r1x, r1y+3.81)
    parts.append(glabel(r1x, r1y - 3.81, "GPIO13", "bidirectional", rot=0))
    parts.append(glabel(r1x, r1y + 3.81, "BTN_LED", "bidirectional", rot=0))

    # ── C1, C2 — Decoupling capacitors ───────────────────────────────
    for ref, val, net_p, cx, cy in [
        ("C1", "100nF", "+3V3", 140, 130),
        ("C2", "100nF", "+5V",  155, 130),
    ]:
        parts.append(f"""  ;; ── {ref} — {val} decoupling ({net_p}) ────────────────────────────────
  (symbol (lib_id "C") (at {cx} {cy} 0) (unit 1)
    (in_bom yes) (on_board yes) (uuid "{uid()}")
    (property "Reference" "{ref}" (id 0) (at {cx+2} {cy} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{val}" (id 1) (at {cx-2} {cy} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (id 2) (at {cx} {cy} 0) (effects (font (size 1.27 1.27)) hide))
  )
""")
        parts.append(pwr_sym(cx, cy - 1.905, net_p))
        parts.append(pwr_sym(cx, cy + 1.905, "GND"))

    parts.append("  (symbol_instances)\n)\n")
    return "".join(parts)


# ── Project file ──────────────────────────────────────────────────────────────

def generate_pro() -> dict:
    return {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.05,
                    "copper_line_width": 0.2,
                    "copper_text_italic": False,
                    "copper_text_size_h": 1.5,
                    "copper_text_size_v": 1.5,
                    "copper_text_thickness": 0.3,
                    "copper_text_upright": False,
                    "courtyard_line_width": 0.05,
                    "fab_line_width": 0.1,
                    "fab_text_italic": False,
                    "fab_text_size_h": 1.0,
                    "fab_text_size_v": 1.0,
                    "fab_text_thickness": 0.15,
                    "fab_text_upright": False,
                    "other_line_width": 0.15,
                    "pads_allow_exempt_soldermask_bridge": False,
                    "silk_line_width": 0.12,
                    "silk_text_italic": False,
                    "silk_text_size_h": 1.0,
                    "silk_text_size_v": 1.0,
                    "silk_text_thickness": 0.15,
                    "silk_text_upright": False,
                },
                "meta": {"version": 2},
                "rules": {
                    "min_clearance": 0.2,
                    "min_copper_edge_clearance": 0.5,
                    "min_hole_clearance": 0.25,
                    "min_hole_to_hole": 0.25,
                    "min_microvia_diameter": 0.2,
                    "min_microvia_drill": 0.1,
                    "min_silk_clearance": 0.0,
                    "min_text_height": 0.5,
                    "min_through_hole_diameter": 0.3,
                    "min_track_width": 0.2,
                    "min_via_annular_width": 0.1,
                    "min_via_diameter": 0.5,
                    "use_height_for_length_calcs": True,
                },
                "track_widths": [],
                "via_dimensions": [],
            },
        },
        "meta": {
            "filename": "pitalk.kicad_pro",
            "version": 1,
        },
        "schematic": {
            "annotate_start_num": 0,
            "meta": {"version": 1},
            "net_format_version": 0,
            "page_layout_descr_file": "",
            "plot_directory": "",
        },
        "sheets": [],
        "text_variables": {},
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import json

    pro_path = PCB_DIR / "pitalk.kicad_pro"
    sch_path = PCB_DIR / "pitalk.kicad_sch"
    pcb_path = PCB_DIR / "pitalk.kicad_pcb"

    pro_path.write_text(json.dumps(generate_pro(), indent=2))
    sch_path.write_text(generate_sch())
    pcb_path.write_text(generate_pcb())

    for p in (pro_path, sch_path, pcb_path):
        sz = p.stat().st_size
        print(f"  wrote {p.relative_to(ROOT)}  ({sz:,} bytes)")


if __name__ == "__main__":
    main()
