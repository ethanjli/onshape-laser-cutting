#!/usr/bin/env python3

import os
import subprocess
import argparse

from lxml import etree

# File path utilities

class FileTypeError(ValueError):
    """Exception raised when attempting to process unsupported file types."""
    pass

def get_file_ext(file_path: str) -> str:
    """Returns the file extension for the provided file path.

    Args:
        file_path: a file path with or without a file extension.

    Returns:
        The file extension, including the leading '.', of file_path. Empty
        string when no file extension exists.
    """
    return os.path.splitext(os.path.basename(file_path))[1]

def get_svg_name(dxf_path: str) -> str:
    """Returns the path the provided dxf file path renamed to an svg file.

    Args:
        dxf_path: a file path, such as for a dxf file.

    Returns:
        A file path which is identical to dxf_path but with a '.svg' file
        extension instead of whatever file extension was in dxf_path.
    """
    (input_name, __) = os.path.splitext(os.path.basename(dxf_path))
    svg_name = input_name + '.svg'
    return svg_name

# Preprocessing

def convert(dxf_path: str, svg_path: str) -> None:
    """Runs Inkscape to import a dxf file and save it as an svg file.

    Args:
        dxf_path: a file path to a dxf file. Must have '.dxf' as its file
            extension.
        svg_path: a file path to the svg file to create.
    """
    subprocess.run(['inkscape', '-l', svg_path, dxf_path])

def style_strokes(svg_path: str, stroke_color: str='#ff0000',
                  stroke_width: float=0.07559055) -> etree.ElementTree:
    """Modifies a svg file so that all black paths become laser cutting paths.

    Args:
        svg_path: a file path to the svg file to modify and overwrite.
        stroke_color: the color, as a hex code, to set paths to.
        stroke_width: the stroke width, in pixels (at 96 pixels per inch), to
            set paths to.

    Returns:
        The modified XML tree.
    """
    xml = etree.parse(svg_path)
    svg = xml.getroot()
    paths = svg.findall('.//{http://www.w3.org/2000/svg}path'
                        '[@style="stroke:#000000;fill:none"]')
    for path in paths:
        path.set('style', (
            'fill:none;stroke:{};stroke-opacity:1;stroke-width:{};'
            'stroke-miterlimit:4;stroke-dasharray:none'
        ).format(stroke_color, stroke_width))
    return xml

def preprocess(dxf_path: str, svg_path: str=None) -> None:
    """Preprocesses the specified dxf file and saves the result.

    Args:
        dxf_path: the path of the dxf file to preprocess. Must end in '.dxf'.
        svg_path: the path of the file to save the preprocessed svg result.
            Defaults to dxf_path, but ending in '.svg' instead of '.dxf'.

    Raises:
        FileTypeError: if dxf_path does not end in '.dxf'.
    """
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
    print('Converted {} to {}.'.format(dxf_path, svg_path))
    xml = style_strokes(svg_path)
    xml.write(svg_path)
    print('Set stroke styles on {}.'.format(svg_path))

def main(input_path: str, output_path: str) -> None:
    """Preprocesses the specified dxf file(s) and saves the result(s).

    Args:
        dxf_path: the path of the dxf file to preprocess, or the directory
            containing the dxf files to preprocess.
        svg_path: the path of the file to save the preprocessed svg result, or
            the path of the directory of the files to save the preprocessed svg
            results. If dxf_path is a single file, defaults to dxf_path, but
            with a '.svg' file extension instead of '.dxf'. If dxf_path is a
            directory, defaults to dxf_path.
    """
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
    parser.add_argument(
        'input', type=str, help=('Path to the DXF file to preprocess, or path to '
                                 'the directory of DXF files to preprocess.')
    )
    parser.add_argument(
        '-o', '--output', type=str, default=None,
        help=('Path to the output SVG file to generate, or path to the intended '
              'parent directory of the output SVG file. Default for a svg input '
              'path: the input path, but with .dxf replaced by .svg. Default '
              'for a directory input path: the input directory.')
    )
    args = parser.parse_args()
    main(args.input, args.output)

