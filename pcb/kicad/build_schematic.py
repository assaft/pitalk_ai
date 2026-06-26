#!/usr/bin/env python3
"""Generate the PiTalk KiCad schematic from the verified PCB wiring."""

from copy import deepcopy
from pathlib import Path
import uuid

from kiutils.items.common import Effects, Font, Position
from kiutils.items.schitems import (
    Connection,
    GlobalLabel,
    NoConnect,
    SchematicSymbol,
    SymbolProjectInstance,
    SymbolProjectPath,
)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib


HERE = Path(__file__).resolve().parent
OUT = HERE / "pitalk.kicad_sch"
SYMLIB = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
PROJECT_UUID = str(uuid.uuid4())

COMPONENTS = [
    {
        "ref": "J1",
        "symbol": "Connector_Generic:Conn_02x20_Odd_Even",
        "value": "RPi_Zero2W",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical",
        "at": (63.5, 85.09),
        "pins": {
            1: "+3V3", 2: "+5V", 3: "TP_SDA", 5: "TP_SCL", 6: "GND",
            7: "TP_INT", 9: "GND", 11: "TP_RST", 12: "I2S_BCLK",
            13: "LCD_RST", 14: "GND", 15: "BTN_SW", 17: "+3V3",
            19: "SPI_MOSI", 20: "GND", 21: "SPI_MISO", 22: "LCD_DC",
            23: "SPI_SCLK", 24: "LCD_CS", 25: "GND", 30: "GND",
            32: "LCD_BL", 33: "BCM13", 34: "GND", 35: "I2S_LRCLK",
            38: "MIC_SD", 39: "GND", 40: "AMP_DIN",
        },
    },
    {
        "ref": "J2",
        "symbol": "Connector_Generic:Conn_01x15",
        "value": "WS_2in_Touch",
        "footprint": "Connector_JST:JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal",
        "at": (127.0, 63.5),
        "pins": {
            1: "+3V3", 3: "GND", 4: "SPI_MISO", 5: "SPI_MOSI",
            6: "SPI_SCLK", 8: "LCD_CS", 9: "LCD_DC", 10: "LCD_RST",
            11: "LCD_BL", 12: "TP_SDA", 13: "TP_SCL", 14: "TP_INT",
            15: "TP_RST",
        },
    },
    {
        "ref": "J3",
        "symbol": "Connector_Generic:Conn_01x07",
        "value": "MAX98357A",
        "footprint": "Connector_PinSocket_2.54mm:PinSocket_1x07_P2.54mm_Vertical",
        "at": (127.0, 114.3),
        "pins": {
            1: "I2S_LRCLK", 2: "I2S_BCLK", 3: "AMP_DIN",
            6: "GND", 7: "+5V",
        },
    },
    {
        "ref": "J4",
        "symbol": "Connector_Generic:Conn_01x03",
        "value": "INMP441_A",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
        "at": (127.0, 139.7),
        "pins": {1: "MIC_SD", 2: "+3V3", 3: "GND"},
    },
    {
        "ref": "J5",
        "symbol": "Connector_Generic:Conn_01x03",
        "value": "INMP441_B",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
        "at": (127.0, 154.94),
        "pins": {1: "GND", 2: "I2S_LRCLK", 3: "I2S_BCLK"},
    },
    {
        "ref": "J6",
        "symbol": "Connector_Generic:Conn_01x04",
        "value": "PB_LED",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        "at": (63.5, 144.78),
        "pins": {1: "BTN_SW", 2: "GND", 3: "LED_A", 4: "GND"},
    },
    {
        "ref": "R1",
        "symbol": "Device:R",
        "value": "330",
        "footprint": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
        "at": (91.44, 144.78),
        "pins": {1: "BCM13", 2: "LED_A"},
    },
    {
        "ref": "C1",
        "symbol": "Device:C_Polarized",
        "value": "10uF",
        "footprint": "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm",
        "at": (91.44, 114.3),
        "pins": {1: "+5V", 2: "GND"},
    },
]


def uid() -> str:
    return str(uuid.uuid4())


def load_symbols():
    libraries = {}
    for nickname, filename in (
        ("Connector_Generic", "Connector_Generic.kicad_sym"),
        ("Device", "Device.kicad_sym"),
    ):
        library = SymbolLib.from_file(SYMLIB / filename)
        libraries[nickname] = {symbol.entryName: symbol for symbol in library.symbols}
    return libraries


def pin_definitions(symbol):
    pins = {}
    for unit in symbol.units:
        for pin in unit.pins:
            pins[int(pin.number)] = pin
    return pins


def pin_position(component, pin):
    x, y = component["at"]
    # Symbol-library coordinates use positive Y upward; schematic sheet
    # coordinates use positive Y downward.
    return Position(x + pin.position.X, y - pin.position.Y)


def label_position(position, angle):
    distance = 5.08
    offsets = {
        0: (-distance, 0),
        90: (0, distance),
        180: (distance, 0),
        270: (0, -distance),
    }
    dx, dy = offsets[int(angle or 0) % 360]
    return Position(position.X + dx, position.Y + dy, angle or 0)


def property_copy(properties, key, value, x, y, hidden=False):
    prop = deepcopy(next(prop for prop in properties if prop.key == key))
    prop.value = value
    prop.position = Position(x, y, 0)
    prop.effects = Effects(font=Font(width=1.27, height=1.27), hide=hidden)
    prop.showName = False
    return prop


def main():
    libraries = load_symbols()
    schematic = Schematic.create_new()
    schematic.version = 20231120
    schematic.generator = "pitalk_schematic_build"
    schematic.uuid = PROJECT_UUID

    embedded = {}
    for component in COMPONENTS:
        nickname, name = component["symbol"].split(":")
        if component["symbol"] not in embedded:
            symbol = deepcopy(libraries[nickname][name])
            symbol.libId = component["symbol"]
            embedded[component["symbol"]] = symbol
            schematic.libSymbols.append(symbol)

        definition = embedded[component["symbol"]]
        pins = pin_definitions(definition)
        x, y = component["at"]
        pin_y = [pin_position(component, pin).Y for pin in pins.values()]
        if component["symbol"].startswith("Connector_Generic:"):
            ref_x = x + 3.81
            ref_y = min(pin_y) - 5.08
            value_x = ref_x
            value_y = ref_y + 2.54
        else:
            ref_x = x + 5.08
            ref_y = y - 2.54
            value_x = ref_x
            value_y = y
        symbol_uuid = uid()
        instance = SchematicSymbol(
            position=Position(x, y, 0),
            unit=1,
            inBom=True,
            onBoard=True,
            uuid=symbol_uuid,
        )
        instance.libId = component["symbol"]
        instance.properties = [
            property_copy(
                definition.properties, "Reference", component["ref"], ref_x, ref_y
            ),
            property_copy(
                definition.properties, "Value", component["value"], value_x, value_y
            ),
            property_copy(
                definition.properties, "Footprint", component["footprint"], x, y, hidden=True
            ),
            property_copy(definition.properties, "Datasheet", "~", x, y, hidden=True),
        ]
        instance.pins = {str(number): uid() for number in pins}
        instance.instances = [
            SymbolProjectInstance(
                name="pitalk",
                paths=[
                    SymbolProjectPath(
                        sheetInstancePath=f"/{PROJECT_UUID}",
                        reference=component["ref"],
                        unit=1,
                    )
                ],
            )
        ]
        schematic.schematicSymbols.append(instance)

        connected = component["pins"]
        for number, pin in pins.items():
            position = pin_position(component, pin)
            if number in connected:
                label_at = label_position(position, pin.position.angle)
                schematic.graphicalItems.append(
                    Connection(
                        type="wire",
                        points=[
                            Position(position.X, position.Y),
                            Position(label_at.X, label_at.Y),
                        ],
                        uuid=uid(),
                    )
                )
                schematic.globalLabels.append(
                    GlobalLabel(
                        text=connected[number],
                        shape="passive",
                        position=label_at,
                        effects=Effects(font=Font(width=1.27, height=1.27)),
                        uuid=uid(),
                    )
                )
            else:
                schematic.noConnects.append(NoConnect(position=position, uuid=uid()))

    schematic.to_file(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
