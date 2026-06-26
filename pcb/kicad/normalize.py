#!/usr/bin/env python3
"""Rewrite a generated board through KiCad's native parser/writer."""

import sys

import pcbnew


path = sys.argv[1]
board = pcbnew.LoadBoard(path)

# Move assembly references into clear silkscreen areas. Library defaults often
# place the reference directly over pin 1 or a mounting-hole pad.
reference_offsets_mm = {
    "J3": (-3.5, 7.5),
    "J4": (3.5, 2.5),
    "J5": (3.5, 2.5),
    "R1": (5.0, -2.5),
    "C1": (0.0, -4.0),
    "H1": (4.0, 0.0),
    "H2": (-4.0, 0.0),
    "H3": (4.0, 0.0),
    "H4": (-4.0, 0.0),
}
for footprint in board.GetFootprints():
    offset = reference_offsets_mm.get(footprint.GetReference())
    if offset:
        reference = footprint.Reference()
        origin = footprint.GetPosition()
        reference.SetPosition(
            pcbnew.VECTOR2I(
                origin.x + pcbnew.FromMM(offset[0]),
                origin.y + pcbnew.FromMM(offset[1]),
            )
        )

pcbnew.SaveBoard(path, board)
