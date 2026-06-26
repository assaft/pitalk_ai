from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "images"

COMPONENTS = {
    "display": {3, 5, 7, 11, 13, 17, 19, 21, 22, 23, 24, 25, 32},
    "amplifier": {2, 6, 12, 35, 40},
    "microphone": {1, 9, 12, 14, 35, 38},
    "button": {15, 33, 34, 39},
}

COLORS = {
    "display": "#1976d2",
    "amplifier": "#d7191c",
    "microphone": "#1b8f3a",
    "button": "#f28c00",
    "unused": "#111111",
}


def diagram(name: str, used_pins: set[int]) -> str:
    width = 420
    height = 790
    left_x = 155
    right_x = 265
    first_y = 115
    row_gap = 31
    radius = 12
    pins = []

    for row in range(20):
        for column in (0, 1):
            pin = row * 2 + column + 1
            x = left_x if column == 0 else right_x
            y = first_y + row * row_gap
            fill = "#d7191c" if pin in used_pins else "#111111"
            label_x = x - 31 if column == 0 else x + 31
            anchor = "end" if column == 0 else "start"
            pins.append(
                f"""
    <circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}"/>
    <text x="{x}" y="{y + 4}" class="pin-number" text-anchor="middle">{pin}</text>
    <text x="{label_x}" y="{y + 5}" class="side-number" text-anchor="{anchor}">{pin}</text>"""
            )

    title = name.capitalize()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{title} Raspberry Pi GPIO pins</title>
  <desc id="description">Raspberry Pi 40-pin header. Pins used by the {name} are red; unused pins are black.</desc>
  <style>
    .title {{ font: 700 24px Arial, sans-serif; fill: #111; }}
    .subtitle {{ font: 14px Arial, sans-serif; fill: #444; }}
    .pin-number {{ font: 700 9px Arial, sans-serif; fill: white; }}
    .side-number {{ font: 12px Arial, sans-serif; fill: #333; }}
    .legend {{ font: 13px Arial, sans-serif; fill: #222; }}
  </style>
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{width / 2}" y="35" class="title" text-anchor="middle">{title} GPIO usage</text>
  <text x="{width / 2}" y="60" class="subtitle" text-anchor="middle">Raspberry Pi Zero 2W — physical pin numbers</text>
  <rect x="125" y="88" width="170" height="620" rx="14" fill="#ededed" stroke="#777" stroke-width="2"/>
  {"".join(pins)}
  <circle cx="115" cy="745" r="9" fill="#d7191c"/>
  <text x="132" y="750" class="legend">Used by {name}</text>
  <circle cx="265" cy="745" r="9" fill="#111111"/>
  <text x="282" y="750" class="legend">Unused</text>
</svg>
"""


def full_wiring_diagram() -> str:
    width = 520
    height = 835
    left_x = 205
    right_x = 315
    first_y = 115
    row_gap = 31
    radius = 12
    pins = []
    pin_components = {
        pin: [name for name, used_pins in COMPONENTS.items() if pin in used_pins]
        for pin in range(1, 41)
    }

    for row in range(20):
        for column in (0, 1):
            pin = row * 2 + column + 1
            x = left_x if column == 0 else right_x
            y = first_y + row * row_gap
            components = pin_components[pin]

            if len(components) == 2:
                left_color = COLORS[components[0]]
                right_color = COLORS[components[1]]
                fill = f"""
    <path d="M {x} {y - radius} A {radius} {radius} 0 0 0 {x} {y + radius} Z" fill="{left_color}"/>
    <path d="M {x} {y - radius} A {radius} {radius} 0 0 1 {x} {y + radius} Z" fill="{right_color}"/>"""
            else:
                color = COLORS[components[0]] if components else COLORS["unused"]
                fill = f"""
    <circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>"""

            label_x = x - 31 if column == 0 else x + 31
            anchor = "end" if column == 0 else "start"
            pins.append(
                f"""{fill}
    <text x="{x}" y="{y + 4}" class="pin-number" text-anchor="middle">{pin}</text>
    <text x="{label_x}" y="{y + 5}" class="side-number" text-anchor="{anchor}">{pin}</text>"""
            )

    legend = [
        ("display", 55, 748),
        ("amplifier", 205, 748),
        ("microphone", 355, 748),
        ("button", 130, 785),
        ("unused", 300, 785),
    ]
    legend_items = "\n".join(
        f"""  <circle cx="{x}" cy="{y}" r="9" fill="{COLORS[name]}"/>
  <text x="{x + 17}" y="{y + 5}" class="legend">{name.capitalize()}</text>"""
        for name, x, y in legend
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Full Raspberry Pi GPIO wiring</title>
  <desc id="description">Raspberry Pi 40-pin header colored by connected component. Shared amplifier and microphone pins are split red and green.</desc>
  <style>
    .title {{ font: 700 24px Arial, sans-serif; fill: #111; }}
    .subtitle {{ font: 14px Arial, sans-serif; fill: #444; }}
    .pin-number {{ font: 700 9px Arial, sans-serif; fill: white; }}
    .side-number {{ font: 12px Arial, sans-serif; fill: #333; }}
    .legend {{ font: 13px Arial, sans-serif; fill: #222; }}
  </style>
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{width / 2}" y="35" class="title" text-anchor="middle">Full GPIO wiring</text>
  <text x="{width / 2}" y="60" class="subtitle" text-anchor="middle">Raspberry Pi Zero 2W — physical pin numbers</text>
  <rect x="175" y="88" width="170" height="620" rx="14" fill="#ededed" stroke="#777" stroke-width="2"/>
  {"".join(pins)}
{legend_items}
</svg>
"""


for component, used_pins in COMPONENTS.items():
    (OUTPUT_DIR / f"gpio-{component}.svg").write_text(
        diagram(component, used_pins),
        encoding="utf-8",
    )

(OUTPUT_DIR / "gpio-full-wiring.svg").write_text(
    full_wiring_diagram(),
    encoding="utf-8",
)
