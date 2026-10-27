#!/usr/bin/env python3

import os
import io
import glob
import json
import math
from PIL import Image
import cairosvg
from rectpack import newPacker


if __name__ == '__main__':
    # sprite.png and sprites.css for html
    svg_files = glob.glob('markers/marker-l-*.svg')
    base_items_cache = []
    for filename in svg_files:
        icon_name = os.path.splitext(os.path.basename(filename))[0]
        svg_path = os.path.join(os.getcwd(), filename)
        try:
            png_bytes = cairosvg.svg2png(url=svg_path, scale=1.0)
            img = Image.open(io.BytesIO(png_bytes))
            base_items_cache.append({'name': icon_name, 'img': img})
        except Exception:
            continue
    base_items_cache.sort(key=lambda it: it['name'])

    tile_w, tile_h = 12, 12
    cols = 16
    n_items = len(base_items_cache)
    if n_items == 0:
        rows = 0
    else:
        rows = int(math.ceil(n_items / float(cols)))
    sheet_w = cols * tile_w
    sheet_h = rows * tile_h if rows > 0 else 0

    sprite_canvas = Image.new('RGBA', (sheet_w, sheet_h), (0, 0, 0, 0))
    positions = {}
    for i, item in enumerate(base_items_cache):
        col = i % cols
        row_idx = i // cols
        x = col * tile_w
        y = row_idx * tile_h
        img = item['img']
        sprite_canvas.paste(img, (x, y))
        suffix = item['name'].replace('marker-l-', '', 1)
        positions[item['name']] = {
            'suffix': suffix,
            'x': x,
            'y': y
        }

    with open('sprite.png', 'wb') as f:
        sprite_canvas.save(f, 'PNG')

    with open('sprites.css', 'w') as f:
        f.write('/* sprite-loader-enable */\n')
        for i, item in enumerate(base_items_cache):
            pos = positions[item['name']]
            suffix = pos['suffix']
            x = pos['x']
            y = pos['y']
            f.write(f".marker-l-{suffix} {{ background-image: url(sprite.png); background-position: -{x}px -{y}px; background-size: {sheet_w}px {sheet_h}px; }}\n")


    # Generate marker-gl-sprite.png and marker-gl-sprite.json for MapLibre GL JS

    svg_sources = []
    svg_sources.extend(glob.glob('markers/marker-b-*.svg'))
    svg_sources.extend(glob.glob('limit.svg'))

    sort_items = []
    for filename in svg_sources:
        icon_name = os.path.splitext(os.path.basename(filename))[0]
        svg_path = os.path.join(os.getcwd(), filename)
        try:
            png_bytes = cairosvg.svg2png(url=svg_path, scale=1.0)
            img = Image.open(io.BytesIO(png_bytes))
            sort_items.append({'name': icon_name, 'path': svg_path, 'h1': img.height})
        except Exception:
            continue

    sort_items.sort(key=lambda it: (-it['h1'], it['name']))

    for pixel_ratio in [1, 2]:
        print(f"generate {pixel_ratio}x")
        items = []
        for it in sort_items:
            try:
                png_bytes = cairosvg.svg2png(url=it['path'], scale=float(pixel_ratio))
                img = Image.open(io.BytesIO(png_bytes))
                items.append({'name': it['name'], 'img': img})
            except Exception:
                continue
        icons_data = items
        w = 64
        h = 64
        rectangles = []
        while True:
            print(f"trying {w}x{h}")
            packer = newPacker(rotation=False)
            for index, item in enumerate(items):
                packer.add_rect(item['img'].width, item['img'].height, index)
            packer.add_bin(w, h)
            packer.pack()
            rectangles = packer.rect_list()
            if len(rectangles) == len(items):
                print("packed all")
                break
            if w >= 4096 and h >= 4096:
                break
            if w < h:
                w *= 2
            else:
                h *= 2
            if w > 8192:
                w = 8192
            if h > 8192:
                h = 8192
        if not rectangles:
            continue
        max_x = max(r[1] + r[3] for r in rectangles)
        max_y = max(r[2] + r[4] for r in rectangles)
        sprite_canvas = Image.new("RGBA", (max_x, max_y), (0, 0, 0, 0))
        sprite_json = {}
        for rect in rectangles:
            _, x, y, width, height, icon_idx = rect
            icon = icons_data[icon_idx]
            img = icon['img']
            sprite_canvas.paste(img, (x, y))
            sprite_json[icon['name']] = {
                "width": width,
                "height": height,
                "x": x,
                "y": y,
                "pixelRatio": pixel_ratio
            }
        suffix = f'@{pixel_ratio}x' if pixel_ratio > 1 else ''
        with open(f'marker-gl-sprite{suffix}.png', 'wb') as f:
            sprite_canvas.save(f, "PNG")
        with open(f'marker-gl-sprite{suffix}.json', 'w') as f:
            json.dump(sprite_json, f)
        print(f"done {suffix}")
