#!/usr/bin/env python3
"""
Generate the PiTalk carrier PCB (4-layer) from the spec in pcb/pcb.md.

Pure-Python: uses `kiutils` (no KiCad `pcbnew` needed). Run with the project
venv:

  .venv/bin/python pcb/kicad/build.py

Routing is done by a small grid (Dijkstra/Lee) maze router. F.Cu, In2.Cu, and
B.Cu carry signal/power traces with through-vias; In1.Cu is reserved as an
uninterrupted GND plane.
"""

import os
import sys
import copy
import heapq
import math
import uuid
import subprocess

from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.brditems import (
    LayerToken,
    Segment,
    Stackup,
    StackupLayer,
    Via,
)
from kiutils.items.gritems import GrLine
from kiutils.items.gritems import GrText
from kiutils.items.zones import Zone, ZonePolygon, Hatch, FillSettings
from kiutils.items.common import Effects, Font, Net, Position

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pitalk.kicad_pcb")
FPLIB = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
KICAD_PYTHON = (
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
    "Python.framework/Versions/3.9/bin/python3"
)

# ----------------------------------------------------------------------------
# Board / rule parameters (mm)
# ----------------------------------------------------------------------------
BOARD_W = 76.0
BOARD_H = 58.0
TRACK_W = 0.25
CLEAR = 0.2
VIA_DIAM = 0.6
VIA_DRILL = 0.3
GRID = 0.635
POWER_WIDTHS = {"+3V3": 0.4, "+5V": 0.4}

# ----------------------------------------------------------------------------
# Components: (ref, value, footprint, x, y, rotation)
# ----------------------------------------------------------------------------
# This placement is intentionally independent from the discarded prototype:
# - Pi socket runs horizontally across the upper half.
# - Display connector exits the lower edge.
# - Microphone headers stay on the left, away from amplifier switching/output.
# - Amplifier and its bulk capacitor are grouped at the right edge.
# - Button connector and resistor are grouped at the lower-left edge.
COMPONENTS = [
    ("J1", "RPi_Zero2W",   "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical", 13.0, 11.0, 90),
    ("J2", "WS_2in_Touch", "Connector_JST:JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal", 38.0, 53.5, 0),
    ("J3", "MAX98357A",    "Connector_PinSocket_2.54mm:PinSocket_1x07_P2.54mm_Vertical", 70.0, 24.0, 0),
    ("J4", "INMP441_A",    "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", 5.0, 25.0, 0),
    ("J5", "INMP441_B",    "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", 5.0, 35.0, 0),
    ("J6", "PB_LED",       "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 14.0, 51.0, 90),
    ("R1", "330",          "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal", 16.0, 45.0, 0),
    ("C1", "10uF",         "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm", 65.0, 43.0, 0),
    ("H1", "M3",           "MountingHole:MountingHole_3.2mm_M3", 3.5, 3.5, 0),
    ("H2", "M3",           "MountingHole:MountingHole_3.2mm_M3", 72.5, 3.5, 0),
    ("H3", "M3",           "MountingHole:MountingHole_3.2mm_M3", 3.5, 54.5, 0),
    ("H4", "M3",           "MountingHole:MountingHole_3.2mm_M3", 72.5, 54.5, 0),
]

# ----------------------------------------------------------------------------
# Netlist: net name -> [(ref, pad), ...]   (mirrors pcb.md "Full wiring")
# ----------------------------------------------------------------------------
NETS = {
    "+3V3":      [("J1", "1"), ("J1", "17"), ("J2", "1"), ("J4", "2")],
    "+5V":       [("J1", "2"), ("J3", "7"), ("C1", "1")],
    "GND":       [("J1", "6"), ("J1", "9"), ("J1", "14"), ("J1", "20"),
                  ("J1", "25"), ("J1", "30"), ("J1", "34"), ("J1", "39"),
                  ("J2", "3"), ("J3", "6"), ("J4", "3"),
                  ("J5", "1"), ("J6", "2"), ("J6", "4"), ("C1", "2")],
    "SPI_MOSI":  [("J1", "19"), ("J2", "5")],
    "SPI_MISO":  [("J1", "21"), ("J2", "4")],
    "SPI_SCLK":  [("J1", "23"), ("J2", "6")],
    "LCD_CS":    [("J1", "24"), ("J2", "8")],
    "LCD_DC":    [("J1", "22"), ("J2", "9")],
    "LCD_RST":   [("J1", "13"), ("J2", "10")],
    "LCD_BL":    [("J1", "32"), ("J2", "11")],
    "TP_SDA":    [("J1", "3"), ("J2", "12")],
    "TP_SCL":    [("J1", "5"), ("J2", "13")],
    "TP_INT":    [("J1", "7"), ("J2", "14")],
    "TP_RST":    [("J1", "11"), ("J2", "15")],
    "I2S_LRCLK": [("J1", "35"), ("J3", "1"), ("J5", "2")],
    "I2S_BCLK":  [("J1", "12"), ("J3", "2"), ("J5", "3")],
    "AMP_DIN":   [("J1", "40"), ("J3", "3")],
    "MIC_SD":    [("J1", "38"), ("J4", "1")],
    "BTN_SW":    [("J1", "15"), ("J6", "1")],
    "BCM13":     [("J1", "33"), ("R1", "1")],
    "LED_A":     [("R1", "2"), ("J6", "3")],
    "unconnected-(J1-Pin_4-Pad4)":   [("J1", "4")],
    "unconnected-(J1-Pin_8-Pad8)":   [("J1", "8")],
    "unconnected-(J1-Pin_10-Pad10)": [("J1", "10")],
    "unconnected-(J1-Pin_16-Pad16)": [("J1", "16")],
    "unconnected-(J1-Pin_18-Pad18)": [("J1", "18")],
    "unconnected-(J1-Pin_26-Pad26)": [("J1", "26")],
    "unconnected-(J1-Pin_27-Pad27)": [("J1", "27")],
    "unconnected-(J1-Pin_28-Pad28)": [("J1", "28")],
    "unconnected-(J1-Pin_29-Pad29)": [("J1", "29")],
    "unconnected-(J1-Pin_31-Pad31)": [("J1", "31")],
    "unconnected-(J1-Pin_36-Pad36)": [("J1", "36")],
    "unconnected-(J1-Pin_37-Pad37)": [("J1", "37")],
    "unconnected-(J2-Pin_2-Pad2)":   [("J2", "2")],
    "unconnected-(J2-Pin_7-Pad7)":   [("J2", "7")],
    "unconnected-(J3-Pin_4-Pad4)":   [("J3", "4")],
    "unconnected-(J3-Pin_5-Pad5)":   [("J3", "5")],
}
POUR_NETS = {"GND"}

ROUTING_LAYERS = ("F.Cu", "In2.Cu", "B.Cu")
GROUND_LAYER = "In1.Cu"


def main():
    board = Board.create_new()
    board.generator = "pitalk_build"
    configure_four_layer_stackup(board)

    # nets: number 1.. (0 is the implicit no-net)
    net_num = {}
    for i, name in enumerate(NETS.keys(), start=1):
        net_num[name] = i
    board.nets = [Net(0, "")] + [Net(net_num[n], n) for n in NETS]

    # footprints
    fps = {}
    for ref, val, fpid, x, y, rotation in COMPONENTS:
        lib, name = fpid.split(":")
        fp = Footprint.from_file(os.path.join(FPLIB, lib + ".pretty", name + ".kicad_mod"))
        fp.libraryNickname = lib
        fp.entryName = name
        # snap origin to the routing grid so 2.54mm-pitch pads land on nodes
        x = round(x / GRID) * GRID
        y = round(y / GRID) * GRID
        fp.position = Position(x, y, rotation)
        fp.layer = "F.Cu"
        fp.tstamp = str(uuid.uuid4())
        fp.properties["Reference"] = ref
        fp.properties["Value"] = val
        if ref.startswith("H"):
            fp.attributes.boardOnly = True
        if ref == "J2":
            # KiCad 10 ships the correct 15-pin footprint but its bundled 3D
            # model set currently stops at 14 pins. Scale the bundled 14-pin
            # male housing to the 15-pin width for a useful 3D representation.
            # This does not alter J2's exact 15-pin copper/assembly footprint.
            fp.models[0].path = (
                "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/"
                "JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal.step"
            )
            fp.models[0].scale.X = 1.06024
        board.footprints.append(fp)
        fps[ref] = fp

    # assign pad nets + collect absolute pad geometry.
    # pad_net is keyed by (ref, number); the obstacle list `pads` carries one
    # entry per *physical* pad (so duplicate numbers like the JST's two "MP"
    # mounting pads are both treated as obstacles).
    pad_net = {}   # (ref,number) -> net name
    pads = []      # list of dicts, one per physical pad
    for name, conns in NETS.items():
        for ref, pad in conns:
            pad_net[(ref, pad)] = name
    for ref, fp in fps.items():
        fx, fy = fp.position.X, fp.position.Y
        # KiCad footprint rotations use the opposite sign from the standard
        # mathematical rotation matrix used for routing coordinates.
        angle = -math.radians(fp.position.angle or 0)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        for p in fp.pads:
            name = pad_net.get((ref, p.number))
            if name is not None:
                p.net = Net(net_num[name], name)
            cu = set()
            for ly in p.layers:
                if ly == "*.Cu":
                    cu.update(range(len(ROUTING_LAYERS)))
                elif ly in ROUTING_LAYERS:
                    cu.add(ROUTING_LAYERS.index(ly))
            px = p.position.X * cos_a - p.position.Y * sin_a
            py = p.position.X * sin_a + p.position.Y * cos_a
            pads.append({
                "ref": ref, "num": p.number,
                "x": fx + px, "y": fy + py,
                "w": p.size.X, "h": p.size.Y,
                "tht": p.drill is not None and getattr(p.drill, "diameter", 0),
                "layers": cu or set(range(len(ROUTING_LAYERS))), "net": name,
            })

    # sanity: report extents
    report_placement(pads)

    # board outline
    corners = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        board.graphicItems.append(
            GrLine(start=Position(*a), end=Position(*b), layer="Edge.Cuts", width=0.15))
    add_pin_labels(board)

    # route + pour
    route(board, pads, net_num)
    board.zones.append(make_pour(net_num["GND"], GROUND_LAYER))

    board.to_file(OUT)
    if os.path.exists(KICAD_PYTHON):
        subprocess.run(
            [KICAD_PYTHON, os.path.join(HERE, "normalize.py"), OUT],
            check=True,
        )
    print("wrote", OUT)


def configure_four_layer_stackup(board):
    """Configure a conventional 1.6 mm four-layer signal/GND/signal stack."""
    # KiCad 9+ uses stable layer IDs rather than the legacy 0..31 copper IDs.
    # Emitting the current file version is required when internal layers are
    # present; mixing legacy IDs with current footprints crashes KiCad 10.
    board.version = 20260206
    board.layers = [
        LayerToken(0, "F.Cu", "signal"),
        LayerToken(4, "In1.Cu", "power"),
        LayerToken(6, "In2.Cu", "signal"),
        LayerToken(2, "B.Cu", "signal"),
        LayerToken(9, "F.Adhes", "user", "F.Adhesive"),
        LayerToken(11, "B.Adhes", "user", "B.Adhesive"),
        LayerToken(13, "F.Paste", "user"),
        LayerToken(15, "B.Paste", "user"),
        LayerToken(5, "F.SilkS", "user", "F.Silkscreen"),
        LayerToken(7, "B.SilkS", "user", "B.Silkscreen"),
        LayerToken(1, "F.Mask", "user"),
        LayerToken(3, "B.Mask", "user"),
        LayerToken(17, "Dwgs.User", "user", "User.Drawings"),
        LayerToken(19, "Cmts.User", "user", "User.Comments"),
        LayerToken(21, "Eco1.User", "user", "User.Eco1"),
        LayerToken(23, "Eco2.User", "user", "User.Eco2"),
        LayerToken(25, "Edge.Cuts", "user"),
        LayerToken(27, "Margin", "user"),
        LayerToken(31, "F.CrtYd", "user", "F.Courtyard"),
        LayerToken(29, "B.CrtYd", "user", "B.Courtyard"),
        LayerToken(35, "F.Fab", "user"),
        LayerToken(33, "B.Fab", "user"),
        LayerToken(39, "User.1", "user"),
        LayerToken(41, "User.2", "user"),
        LayerToken(43, "User.3", "user"),
        LayerToken(45, "User.4", "user"),
    ]
    board.general.thickness = 1.6
    board.setup.stackup = Stackup(
        layers=[
            StackupLayer(name="F.Cu", type="copper", thickness=0.035),
            StackupLayer(
                name="dielectric 1", type="prepreg", thickness=0.18,
                material="FR4", epsilonR=4.5, lossTangent=0.02,
            ),
            StackupLayer(name="In1.Cu", type="copper", thickness=0.035),
            StackupLayer(
                name="dielectric 2", type="core", thickness=1.10,
                material="FR4", epsilonR=4.5, lossTangent=0.02,
            ),
            StackupLayer(name="In2.Cu", type="copper", thickness=0.035),
            StackupLayer(
                name="dielectric 3", type="prepreg", thickness=0.18,
                material="FR4", epsilonR=4.5, lossTangent=0.02,
            ),
            StackupLayer(name="B.Cu", type="copper", thickness=0.035),
        ],
        copperFinish="ENIG",
        dielectricContraints="no",
    )


def report_placement(pads):
    xs = [p["x"] for p in pads]
    ys = [p["y"] for p in pads]
    print("pad X range %.1f..%.1f  Y range %.1f..%.1f (board %gx%g)"
          % (min(xs), max(xs), min(ys), max(ys), BOARD_W, BOARD_H))
    if min(xs) < 1 or max(xs) > BOARD_W - 1 or min(ys) < 1 or max(ys) > BOARD_H - 1:
        print("  WARNING: pads near/over board edge")


def add_pin_labels(board):
    """Add assembly-facing pin names to the connector silkscreen."""

    def text(label, x, y, angle=0, size=0.8):
        board.graphicItems.append(GrText(
            text=label,
            position=Position(x, y, angle),
            layer="F.SilkS",
            effects=Effects(font=Font(width=size, height=size, thickness=0.12)),
            tstamp=str(uuid.uuid4()),
        ))

    # Microphone headers: labels sit to the right of each pin, away from board edge.
    for y, label in ((24.765, "SD"), (27.305, "3V3"), (29.845, "GND")):
        text(label, 10.9, y + 0.25)
    for y, label in ((34.925, "GND"), (37.465, "LRC"), (40.005, "BCLK")):
        text(label, 10.9, y + 0.25)

    # Button/LED header: the connector is horizontal, so vertical labels fit below it.
    for x, label in ((13.97, "SW"), (16.51, "GND"), (19.05, "LED"), (21.59, "GND")):
        text(label, x, 55.0, angle=90)

    # Amplifier socket: labels sit to the left of the socket to avoid the board edge.
    for y, label in (
        (24.13, "LRC"),
        (26.67, "BCLK"),
        (29.21, "DIN"),
        (31.75, "NC"),
        (34.29, "NC"),
        (36.83, "GND"),
        (39.37, "5V"),
    ):
        text(label, 61.5, y + 0.25)

    # Pi header orientation and high-risk power/I2S endpoints.
    text("PIN1", 7.0, 8.0)
    text("1=3V3  2=5V", 18.0, 6.2)
    text("39=GND 40=DIN", 59.0, 15.0)


# ----------------------------------------------------------------------------
# Maze router (three routing layers; In1.Cu remains a solid GND plane)
# ----------------------------------------------------------------------------
LAYER_NAME = ROUTING_LAYERS


def route(board, pads, net_num):
    nx = int(BOARD_W / GRID) + 1
    ny = int(BOARD_H / GRID) + 1
    layer_count = len(LAYER_NAME)
    occ = [[[None] * ny for _ in range(nx)] for _ in range(layer_count)]
    # vset[i][j] = set of pad nets ("#"=NC pad or drilled hole) whose via
    # keepout covers this cell. A via for net N is allowed only if every entry
    # equals N (a via needs no clearance to its own net's pad, but must clear
    # other nets' copper and every drilled hole).
    vset = [[set() for _ in range(ny)] for _ in range(nx)]

    def cell(x, y):
        return (max(0, min(nx - 1, int(round(x / GRID)))),
                max(0, min(ny - 1, int(round(y / GRID)))))

    def xy(i, j):
        return (i * GRID, j * GRID)

    # Pass 1: stamp pad clearance halos (Euclidean, so tracks can still pass
    # between 2.54mm-pitch pads). Conflicting coverage becomes a hard block.
    # Also mark a no-via keepout around drilled holes (hole-to-hole clearance).
    pad_cells = {}      # (ref,num) -> (ci,cj)  [signal pads are unique]
    pad_layers = {}     # (ref,num) -> copper layer set
    for pad in pads:
        ci, cj = cell(pad["x"], pad["y"])
        key = (pad["ref"], pad["num"])
        pad_cells[key] = (ci, cj)
        pad_layers[key] = pad["layers"]
        owner = pad["net"]
        padr = max(pad["w"], pad["h"]) / 2.0
        halo = padr + CLEAR + TRACK_W / 2.0       # track-clearance to this pad
        vkeep = padr + CLEAR + VIA_DIAM / 2.0     # via-copper clearance to pad
        hkeep = (pad["tht"] / 2.0 + 0.25 + VIA_DRILL / 2.0) if pad["tht"] else 0
        r = int(max(halo, vkeep, hkeep) / GRID + 0.999)
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                i, j = ci + di, cj + dj
                if not (0 <= i < nx and 0 <= j < ny):
                    continue
                dist = math.hypot(i * GRID - pad["x"], j * GRID - pad["y"])
                if dist <= vkeep:
                    vset[i][j].add(owner if owner else "#")
                if dist <= hkeep:
                    vset[i][j].add("#")           # hole-to-hole: blocks all nets
                if dist > halo:
                    continue
                for L in range(layer_count):
                    cur = occ[L][i][j]
                    if cur is None:
                        occ[L][i][j] = owner if owner else "#"
                    elif not (owner and cur == owner):
                        occ[L][i][j] = "#"

    # Pass 2: force each pad's own centre cell to its net on the copper layers
    # it actually lives on (THT=both, SMD=one). Guarantees an escape node a
    # later halo can't overwrite, and stops the router from "connecting" to an
    # SMD pad on the wrong layer.
    for pad in pads:
        owner = pad["net"]
        if not owner:
            continue
        ci, cj = cell(pad["x"], pad["y"])
        for L in range(layer_count):
            occ[L][ci][cj] = owner if L in pad["layers"] else "#"

    # Pass 3: board-edge keepout (copper-to-edge clearance; vias need more).
    edge_m = 0.8
    for i in range(nx):
        for j in range(ny):
            x, y = i * GRID, j * GRID
            if x < edge_m or x > BOARD_W - edge_m or y < edge_m or y > BOARD_H - edge_m:
                vset[i][j].add("#")
                for L in range(layer_count):
                    if occ[L][i][j] is None:
                        occ[L][i][j] = "#"

    base_occ = occ
    traces = []
    VIA_COST = 20

    def via_clear(i, j, net):
        """A through-via must clear copper already routed on every layer."""
        radius = VIA_DIAM / 2.0 + CLEAR + max(POWER_WIDTHS.values()) / 2.0
        cells = int(radius / GRID + 0.999)
        for di in range(-cells, cells + 1):
            for dj in range(-cells, cells + 1):
                if math.hypot(di * GRID, dj * GRID) > radius:
                    continue
                ni, nj = i + di, j + dj
                if not (0 <= ni < nx and 0 <= nj < ny):
                    return False
                for layer in range(layer_count):
                    owner = occ[layer][ni][nj]
                    if owner is not None and owner != net:
                        return False
        return True

    def dijkstra(sources, targets, net):
        tset = set(targets)
        dist, prev, pq = {}, {}, []
        for s in sources:
            dist[s] = 0
            heapq.heappush(pq, (0, s))
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, 1e18):
                continue
            if u in tset:
                path = [u]
                while u in prev:
                    u = prev[u]
                    path.append(u)
                return path[::-1]
            i, j, L = u
            cand = [(i + 1, j, L, 1), (i - 1, j, L, 1),
                    (i, j + 1, L, 1), (i, j - 1, L, 1)]
            if (all(o == net for o in vset[i][j])
                    and via_clear(i, j, net)):         # through-via allowed?
                cand.extend(
                    (i, j, other, VIA_COST)
                    for other in range(layer_count)
                    if other != L
                )
            for ni_, nj_, nl_, w in cand:
                if not (0 <= ni_ < nx and 0 <= nj_ < ny):
                    continue
                o = occ[nl_][ni_][nj_]
                if o is not None and o != net:
                    continue
                v = (ni_, nj_, nl_)
                nd = d + w
                if nd < dist.get(v, 1e18):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return None

    def commit(path, net):
        for (i, j, L) in path:
            if occ[L][i][j] in (None, net):
                occ[L][i][j] = net
        run = [path[0]]
        for k in range(1, len(path)):
            if path[k][2] != path[k - 1][2]:
                flush(run, net)
                i, j, _ = path[k]
                add_via(xy(i, j), net)
                run = [path[k]]
            else:
                run.append(path[k])
        flush(run, net)

    def flush(run, net):
        if len(run) < 2:
            return
        L = run[0][2]
        start = run[0]
        for k in range(1, len(run)):
            if k + 1 < len(run):
                a, b, c = run[k - 1], run[k], run[k + 1]
                if (b[0] - a[0], b[1] - a[1]) == (c[0] - b[0], c[1] - b[1]):
                    continue
            add_seg(xy(start[0], start[1]), xy(run[k][0], run[k][1]), LAYER_NAME[L], net)
            start = run[k]

    def add_seg(p1, p2, layer, net):
        traces.append(Segment(
            start=Position(p1[0], p1[1]), end=Position(p2[0], p2[1]),
            width=POWER_WIDTHS.get(net, TRACK_W),
            layer=layer, net=net_num[net], tstamp=str(uuid.uuid4())))

    def add_via(p, net):
        traces.append(Via(
            position=Position(p[0], p[1]), size=VIA_DIAM, drill=VIA_DRILL,
            layers=["F.Cu", "B.Cu"], net=net_num[net], tstamp=str(uuid.uuid4())))
        # reserve a clearance halo so other nets keep via-to-via/track distance
        vhalo = VIA_DIAM / 2.0 + CLEAR + VIA_DIAM / 2.0
        ci, cj = cell(p[0], p[1])
        r = int(vhalo / GRID + 0.999)
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                i, j = ci + di, cj + dj
                if (0 <= i < nx and 0 <= j < ny
                        and math.hypot(i * GRID - p[0], j * GRID - p[1]) <= vhalo):
                    for L in range(layer_count):
                        if occ[L][i][j] is None:
                            occ[L][i][j] = net

    def run_order(order):
        nonlocal occ, traces
        occ = copy.deepcopy(base_occ)
        traces = []
        for name in order:
            cells = [pad_cells[(r, p)] for (r, p) in NETS[name]]
            tree = set()
            ci, cj = cells[0]
            tree.update((ci, cj, L) for L in range(layer_count))
            for (ti, tj) in cells[1:]:
                path = dijkstra(
                    list(tree),
                    [(ti, tj, L) for L in range(layer_count)],
                    name,
                )
                if path is None:
                    return name
                commit(path, name)
                tree.update(path)
                tree.update((ti, tj, L) for L in range(layer_count))
        return None

    # route, reordering on failure (push the blocked net earlier and retry).
    # GND has the most pads, so route it first; the pour is a bonus on top.
    order = sorted(NETS, key=lambda n: 0 if n == "GND" else 1)
    fail = "x"
    for _ in range(len(order) * 3):
        fail = run_order(order)
        if fail is None:
            break
        order.remove(fail)
        order.insert(0, fail)
    if fail is None:
        board.traceItems.extend(traces)
        print("all nets routed (%d trace items)" % len(traces))
    else:
        board.traceItems.extend(traces)
        print("ROUTING FAILED for:", fail)


def make_pour(netnum, layer):
    z = Zone()
    z.net = netnum
    z.netName = "GND"
    z.layers = [layer]
    z.hatch = Hatch(style="edge", pitch=0.5)
    z.connectPads = "yes"   # solid pad connection (no thermal reliefs)
    z.clearance = CLEAR
    z.minThickness = 0.25
    z.fillSettings = FillSettings(yes=True, thermalGap=0.5, thermalBridgeWidth=0.5)
    m = 0.5
    pts = [(m, m), (BOARD_W - m, m), (BOARD_W - m, BOARD_H - m), (m, BOARD_H - m)]
    z.polygons = [ZonePolygon(coordinates=[Position(x, y) for (x, y) in pts])]
    return z


if __name__ == "__main__":
    main()
