#!/usr/bin/env python3

import os
import subprocess
import argparse

from lxml import etree

# File path utilities

class FileTypeError(ValueError):
    pass

def get_file_ext(file_path):
    return os.path.splitext(os.path.basename(file_path))[1]

def get_svg_name(dxf_path):
    (input_name, __) = os.path.splitext(os.path.basename(dxf_path))
    svg_name = input_name + '.svg'
    return svg_name

# Preprocessing

def convert(dxf_path, svg_path):
    subprocess.run(['inkscape', '-l', svg_path, dxf_path])
    print('Converted {} to {}.'.format(dxf_path, svg_path))
    return svg_path

def style_strokes(svg_path, stroke_color='#ff0000', stroke_width='0.07559055'):
    xml = etree.parse(svg_path)
    svg = xml.getroot()
    paths = svg.findall('.//{http://www.w3.org/2000/svg}path'
                        '[@style="stroke:#000000;fill:none"]')
    for path in paths:
        path.set('style', (
            'fill:none;stroke:{};stroke-opacity:1;stroke-width:{};'
            'stroke-miterlimit:4;stroke-dasharray:none'
        ).format(stroke_color, stroke_width))

    xml.write(svg_path)
    print('Set stroke styles on {}.'.format(svg_path))

def preprocess(dxf_path, svg_path=None):
    dxf_ext = get_file_ext(dxf_path)
    if dxf_ext != '.dxf':
        raise FileTypeError('Unsupported file extension {} on input file {}!'
                            .format(dxf_ext, dxf_path))
    if svg_path is None:
        parent_path = os.path.dirname(dxf_path)
        svg_path = os.path.join(parent_path, get_svg_name(dxf_path))
    elif not get_file_ext(svg_path):
        parent_path = svg_path
        svg_path = os.path.join(parent_path, get_svg_name(dxf_path))
    convert(dxf_path, svg_path)
    style_strokes(svg_path)

def main(input_path, output_path):
    input_ext = get_file_ext(input_path)
    if input_ext:
        preprocess(input_path, output_path)
        return
    for filename in os.listdir(input_path):
        input_ext = get_file_ext(filename)
        try:
            preprocess(os.path.join(input_path, filename), output_path)
        except FileTypeError:
            print('Skipped {}'.format(filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Preprocess an Onshape DXF drawing export for laser cutting.'
    )
    parser.add_argument('input', type=str,
                        help=('Path to the DXF file to preprocess, or path to '
                              'the directory of DXF files to preprocess.'))
    parser.add_argument('-o', '--output', type=str, default=None,
                        help=('Path to the output SVG file to generate, or path to '
                              'the intended parent directory of the output SVG file.'
                              'Default for a single-file input: the input path, '
                              'but with .dxf replaced by .svg.'
                              'Default for a directory input: the input path.'))
    args = parser.parse_args()
    main(args.input, args.output)

