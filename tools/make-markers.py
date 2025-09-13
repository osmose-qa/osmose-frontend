#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import subprocess

from modules import query_meta
from modules.dependencies import database

# # Symboles

# O point
# L diamond
# K square
# P plus
# M minus
# F cross
# = equal sign
# | vertical line
# || double vertical line
# :: four dots
# .:. four dots in diamond
# T tiangle up
# tiangle down
# X hourglass
# >< hourglass lying
# L'
# .l
# [] empty square
# . dot
# '. two small squares
# / diagonal
# =-
# H H
# h H at 90°
# Dd two half-circle


def get_symb(symbole):
    if symbole == "O":
        return "<circle cx='8' cy='8' r='3' />"
    if symbole == "L":
        return "<path d='M 8,12 L 4,8 L 8,4 L 12,8 L 8,12 z' />"
    if symbole == "K":
        return "<path d='M 11,11 L 5,11 L 5,5 L 11,5 L 11,11 z' />"
    if symbole == "P":
        l1 = "<path d='M 9,11 L 7,11 L 7,5 L 9,5 L 9,11 z' />"
        l2 = "<path d='M 11,9 L 5,9 L 5,7 L 11,7 L 11,9 z' />"
        return l1 + l2
    if symbole == "F":
        l1 = (
            "<path transform='rotate(45 8 8)' d='M 9,12 L 7,12 L 7,4 L 9,4 L 9,12 z' />"
        )
        l2 = (
            "<path transform='rotate(45 8 8)' d='M 12,9 L 4,9 L 4,7 L 12,7 L 12,9 z' />"
        )
        return l1 + l2
    if symbole == "M":
        return "<path d='M 11,9 L 5,9 L 5,7 L 11,7 L 11,9 z' />"
    if symbole == "=":
        l1 = "<path d='M 11,9 L 5,9 L 5,11 L 11,11 L 11,9 z' />"
        l2 = "<path d='M 11,7 L 5,7 L 5,5 L 11,5 L 11,7 z' />"
        return l1 + l2
    if symbole == "|":
        return "<path d='M 9,11 L 7,11 L 7,5 L 9,5 L 9,11 z' />"
    if symbole == "||":
        l1 = "<path transform='rotate(90 8 8)' d='M 11,9 L 5,9 L 5,11 L 11,11 L 11,9 z' />"
        l2 = (
            "<path transform='rotate(90 8 8)' d='M 11,7 L 5,7 L 5,5 L 11,5 L 11,7 z' />"
        )
        return l1 + l2
    if symbole == "::":
        l1 = "<path d='M 11,9 L 9,9 L 9,11 L 11,11 L 11,9 z' />"
        l2 = "<path d='M 11,7 L 9,7 L 9,5 L 11,5 L 11,7 z' />"
        l3 = "<path d='M 7,9 L 5,9 L 5,11 L 7,11 L 7,9 z' />"
        l4 = "<path d='M 7,7 L 5,7 L 5,5 L 7,5 L 7,7 z' />"
        return l1 + l2 + l3 + l4
    if symbole == ".:.":
        l1 = "<path d='M 11,9 L 9,9 L 9,11 L 11,11 L 11,9 z' />"
        l2 = "<path d='M 11,7 L 9,7 L 9,5 L 11,5 L 11,7 z' />"
        l3 = "<path d='M 7,9 L 5,9 L 5,11 L 7,11 L 7,9 z' />"
        l4 = "<path d='M 7,7 L 5,7 L 5,5 L 7,5 L 7,7 z' />"
        return "<g transform='rotate(45 8 8)'>" + l1 + l2 + l3 + l4 + "</g>"
    if symbole == "T":
        return "<path d='M 5,11 L 5,5 L 11,5 L 5,11 z' />"
    if symbole == "t":
        return "<path d='M 11,11 L 5,11 L 11,5 L 11,11 z' />"
    if symbole == "X":
        return "<path d='M 11,11 L 5,11 L 11,5 L 5,5 L 11,11 z' />"
    if symbole == "><":
        return "<path d='M 11,11 L 11,5 L 5,11 L 5,5 L 11,11 z' />"
    if symbole == "L'":
        l1 = "<path d='M 5,5 L 11,5 L 11,7 L 7,7 L 7,11 L 5,11 z' />"
        l2 = "<path d='M 11,11 L 9,11 L 9,9 L 11,9 z' />"
        return l1 + l2
    if symbole == ".l":
        l1 = "<path d='M 11,11 L 11,5 L 9,5 L 9,9 L 5,9 L 5,11 z' />"
        l2 = "<path d='M 5,5 L 7,5 L 7,7 L 5,7 z' />"
        return l1 + l2
    if symbole == "[]":
        return "<path d='M 5,5 L 11,5 L 11,11 L 5,11 z M 7,7 L 7,9 L 9,9 L 9,7 z' />"
    if symbole == ".":
        return "<path d='M 7,7 L 7,9 L 9,9 L 9,7 z' />"
    if symbole == "'.":
        l1 = "<path d='M 11,8 L 8,8 L 8,11 L 11,11 L 11,8 z' />"
        l2 = "<path d='M 8,8 L 5,8 L 5,5 L 8,5 L 8,8 z' />"
        return l1 + l2
    if symbole == "/":
        return (
            "<path transform='rotate(45 8 8)' d='M 9,12 L 7,12 L 7,4 L 9,4 L 9,12 z' />"
        )
    if symbole == "=-":
        l1 = "<path d='M 11,9 L 8,9 L 8,7 L 11,7 L 11,9 z' />"
        l2 = "<path d='M 8,7 L 5,7 L 5,5 L 8,5 L 8,7 z' />"
        l3 = "<path d='M 8,11 L 5,11 L 5,9 L 8,9 L 8,11 z' />"
        return l1 + l2 + l3
    if symbole == "H":
        return "<path d='M 5,5 L 7,5 L 7,7 L 9,7 L 9,5 L 11,5 L 11,11 L 9,11 L 9,9 L 7,9 L 7,11 L 5,11 z' />"
    if symbole == "h":
        return (
            "<path transform='rotate(90 8 8)' "
            + "d='M 5,5 L 7,5 L 7,7 L 9,7 L 9,5 L 11,5 L 11,11 L 9,11 L 9,9 L 7,9 L 7,11 L 5,11 z' />"
        )


# Markers

# M Map Marker
# L Legend


def get_marker(contour, symbole, couleur):
    dark_color = "#%0.2X%0.2X%0.2X" % (
        int(int(couleur[1:3], 16) * 0.5),
        int(int(couleur[3:5], 16) * 0.5),
        int(int(couleur[5:7], 16) * 0.5),
    )
    mid_color = "#%0.2X%0.2X%0.2X" % (
        int(int(couleur[1:3], 16) * 0.75),
        int(int(couleur[3:5], 16) * 0.75),
        int(int(couleur[5:7], 16) * 0.75),
    )
    if contour == "L":  # Legend
        height = 12
        width = height
        g = "translate(-2,-2) scale(1,1)"
        c = f"""
<defs id='defs'>
    <linearGradient id='gradient' x1='6' y1='12' x2='6' y2='0' gradientUnits='userSpaceOnUse'>
    <stop style='stop-color:{mid_color}' offset='0' />
    <stop style='stop-color:{couleur}' offset='1' />
    </linearGradient>
</defs>
<path style='fill:url(#gradient);'
    d='M 0.5,0.5 L 0.5,11.5 L 11.5,11.5 L 11.5,0.5 L 0.5,0.5 z' />
<path style='fill:none;stroke:{mid_color};stroke-width:1px'
    d='M 1.5,1.5 L 1.5,10.5 L 10.5,10.5 L 10.5,1.5 L 1.5,1.5 z' />
<path style='fill:none;stroke:#000000;stroke-width:1px'
    d='M 0.5,0.5 L 0.5,11.5 L 11.5,11.5 L 11.5,0.5 L 0.5,0.5 z' />
"""
        m = get_symb(symbole)
    if contour == "B":  # bubble
        height = 32
        width = 16
        g = "translate(0,1) scale(1,1)"
        c = f"""
<defs id='defs'>
    <linearGradient id='gradient' x1='8' y1='32' x2='8' y2='0' gradientUnits='userSpaceOnUse'>
    <stop style='stop-color:{dark_color}' offset='0' />
    <stop style='stop-color:{couleur}' offset='1' />
    </linearGradient>
</defs>
<path style='fill:url(#gradient)'
    d='m 8,31.75 c 2,-12 7.75,-18 7.75,-23.5 0,-4 -3.5,-8 -7.75,-8 -4.25,0 -7.75,4 -7.75,8 0,5.5
        5.75,11.5 7.75,23.5 z' />
<path style='fill:none;stroke:{mid_color}";stroke-width:.75px'
    d='m 8,0.5 c -4.0986579,0 -7.5,3.8907009 -7.5,7.75 0,2.665945 1.4044222,5.527256 3.09375,9.21875
        1.5774956,3.44712 3.3559017,7.676923 4.40625,13.125 1.0503483,-5.448077 2.828754,-9.67788
        4.40625,-13.125 C 14.095578,13.777256 15.5,10.915945 15.5,8.25 15.5,4.3907009 12.098658,0.58,0.5 z' />
<path style='fill:none;stroke:#000000;stroke-width:.5px'
    d='m 8,31.75 c 2,-12 7.75,-18 7.75,-23.5 0,-4 -3.5,-8 -7.75,-8 -4.25,0 -7.75,4 -7.75,8 0,5.5
        5.75,11.5 7.75,23.5 z' />
"""
        m = get_symb(symbole)
    head = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    head += (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'
        + str(width)
        + '" height="'
        + str(height)
        + '">\n'
    )
    tail = "</svg>"
    return (
        head
        + c
        + "\n<g transform='"
        + g
        + "' style='fill:#000000;'>\n"
        + m
        + "</g>\n"
        + tail
    )


async def main():
    db = await database.get_dbconn()
    all_items = []
    for g in await query_meta._items(db):
        all_items += g["items"]
    # all_items = [{"item":9999, "marker_flag":"=-", "marker_color":"#ff0000"}] # Test

    marker_folder = os.path.join("..", "api", "assets", "markers")
    subprocess.getstatusoutput("rm " + os.path.join(marker_folder, "*.png"))
    css = "/* sprite-loader-enable */\n"
    for i in all_items:
        print(i)
        for m in "LB":
            file_svg = os.path.join(
                marker_folder, f"marker-{m.lower()}-{i['item']}.svg"
            )
            file_png = os.path.join(
                marker_folder, f"marker-{m.lower()}-{i['item']}.png"
            )
            open(file_svg, "w").write(get_marker(m, i["flag"], i["color"]))
            # subprocess.getstatusoutput(f"rsvg {file_svg} {file_png}")
            subprocess.getstatusoutput(f"rsvg-convert {file_svg} > {file_png}")
        css += ".marker-l-{0} {{ background-image: url(marker-l-{0}.png); }}\n".format(
            i["item"]
        )
    open(os.path.join(marker_folder, "markers-l.css"), "w").write(css)


if __name__ == "__main__":
    asyncio.run(main())
