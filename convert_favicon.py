#!/usr/bin/env python3
"""
Convert SVG favicon to ICO format
Run this script to generate favicon.ico from favicon.svg
"""

import cairosvg
from PIL import Image
import os

def convert_svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48]):
    """Convert SVG to multi-size ICO file"""

    # Convert SVG to PNG at different sizes
    png_files = []
    for size in sizes:
        png_path = f"temp_favicon_{size}.png"
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
        png_files.append(png_path)

    # Create ICO from PNG files
    images = [Image.open(png) for png in png_files]
    images[0].save(ico_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])

    # Clean up temporary PNG files
    for png in png_files:
        os.remove(png)

    print(f"✅ Favicon converted: {ico_path}")

if __name__ == "__main__":
    convert_svg_to_ico("static/favicon.svg", "static/favicon.ico")