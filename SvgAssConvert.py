"""
File: SvgAssConvert.py
Language: Python3
Author: 9volt <ninevult@gmail.com>
Purpose:
    Convert vector SVG files to the Advanced Substation Alpha (*.ass)
    format for use by advanced anime typesetters.
"""

# Imports
import sys
import os
from xml.etree import ElementTree


# Global variables
NAME = "SvgAssConvert"
VERSION = str(0.2)
VERBOSE = False

input_file = ""
output_file = ""
out_file = None

layer = 1


def read_input():
    """
    Reads through the input file using ElementTree to extract
    the commands, then send the arguments to be processed individually
    :return: None
    """
    tree = ElementTree.parse(input_file)
    root = tree.getroot()

    for child in root:
        if child.tag.startswith("{http://www.w3.org/2000/svg}"):
            command = child.tag[28:]
        else:
            command = child.tag

        # Select appropriate function for the task
        if command == "line":
            line(child.attrib)
        elif command == "polyline":
            polyline(child.attrib)
        elif command == "rect":
            rect(child.attrib)
        elif command == "circle":
            circle(child.attrib)
        elif command == "ellipse":
            ellipse(child.attrib)
        #if command == "path":
        #    path(child.attrib)


# region Shape Generators

def line(attribs):
    """
    Generates a line
    Required attributes:
        x1:      Origin x-coordinate
        x2:      Destination x-coordinate
        y1:      Origin y-coordinate
        y1:      Destination y-coordinate
    :param attribs: Parameters for creating the line
    :return: None
    """
    x1 = attribs.get("x1")
    y1 = attribs.get("y1")
    x2 = attribs.get("x2")
    y2 = attribs.get("y2")
    fill, stroke = parse_style(attribs)
    generator = \
        "m", x1, y1, \
        "l", x1, \
        "l", y1, x2, y2

    generator = " ".join(generator)
    add_line(generator, "line", fill, stroke)


def polyline(attribs):
    """
    Generates a polyline
    Required attributes:
        points:     List of coordinates for lines
    :param attribs: Parameters for creating the line
    :return: None
    """
    points = str(attribs.get("points")).replace(" ", ",").replace(",,", ",").split(",")
    fill, stroke = parse_style(attribs)
    generator = ["m", points[0], points[1]]
    for i in range(0, len(points)):
        if i % 2 == 0:
            generator.append("l")
            generator.append(points[i])
        else:
            generator.append(points[i])

    generator = " ".join(generator)
    add_line(generator, "polyline", fill, stroke)


def rect(attribs):
    """
    Generates a rectangle
    Required attributes:
        x:      Origin x-coordinate
        y:      Origin y-coordinate
        width:  Width of the rectangle
        height: Height of the rectangle
    :param attribs: Parameters for creating the rectangle
    :return: None
    """
    x = attribs.get("x")
    y = attribs.get("y")
    width = attribs.get("width")
    height = attribs.get("height")
    fill, stroke = parse_style(attribs)
    generator = \
        "m", x, y, \
        "l", x, y, \
        "l", strsum(x, width), y, \
        "l", strsum(x, width), strsum(y, height), \
        "l", x, strsum(y, height)

    generator = " ".join(generator)
    add_line(generator, "rect", fill, stroke)


def circle(attribs):
    """
    Generates a circle
    Required attributes:
        cx: Origin x-coordinate
        yy: Origin y-coordinate
        r:  Radius of the circle
    :param attribs: Parameters for creating the circle
    :return: None
    """
    x = attribs.get("cx")
    y = attribs.get("cy")
    r = attribs.get("r")
    fill, stroke = parse_style(attribs)
    generator = \
        "m", x, y, \
        "b", x, y,                              strsum(x, r), y,                    strsum(x, r), strsum(y, r), \
        "b", strsum(x, r), strsum(y, r),        strsum(x, r), strsum(y, r, r),      x, strsum(y, r, r), \
        "b", x, strsum(y, r, r),                strsub(x, r), strsum(y, r, r),      strsub(x, r), strsum(y, r), \
        "b", strsub(x, r), strsum(y, r),        strsub(x, r), y,                    x, y

    generator = " ".join(generator)
    add_line(generator, "circle", fill, stroke)


def ellipse(attribs):
    """
    Generates an ellipse
    Required attributes:
        cx:  Origin x-coordinate
        yy:  Origin y-coordinate
        rx:  Radius on the x-axis
        ry:  Radius on the y-axis
    :param attribs: Parameters for creating the ellipse
    :return: None
    """
    x = attribs.get("cx")
    y = attribs.get("cy")
    rx = attribs.get("rx")
    ry = attribs.get("ry")
    fill, stroke = parse_style(attribs)
    generator = \
        "m", x, y, \
        "b", x, y,                              strsum(x, rx), y,                       strsum(x, rx), strsum(y, ry), \
        "b", strsum(x, rx), strsum(y, ry),      strsum(x, rx), strsum(y, ry, ry),       x, strsum(y, ry, ry), \
        "b", x, strsum(y, ry, ry),              strsub(x, rx), strsum(y, ry, ry),       strsub(x, rx), strsum(y, ry), \
        "b", strsub(x, rx), strsum(y, ry),      strsub(x, rx), y,                       x, y
    generator = " ".join(generator)
    add_line(generator, "ellipse", fill, stroke)


def path(attribs):  # TODO
    """
    Draws according to a SVG Path
    :param attribs: Parameters for creating the path
    :return: None
    """
    d = attribs.get("d")
    lines = d.split("\n")

    x = y = 0

    for lin in lines:
        cmd = lin[:1]  # first character
        params = lin[1:]

        if cmd == "M" or cmd == "m":
            split = params.split(",")
            x = split[0]
            y = split[1]

            print(x)
            print(y)

# endregion


# region File I/O

def add_line(text, name, fill, stroke):
    """
    Generates a usable line for the ASS format
    :param text: Text to be "displayed"
    :param name: Name to be used in the Actor field
    :param stroke: Outline color
    :param fill: Fill color
    :return: None
    """
    global layer
    out_file.write("Dialogue: " + str(layer) + ",0:00:00.0,0:00:02.00,SVG," + name + ",0,0,0,," +
                   "{\\c&H" + fill + "&\\3c&H" + stroke + "&}{\\p1+}" + text + "{\\p0}\n")
    layer += 1


def generate_file():
    """
    Generates ASS File template
    :return: None
    """
    global out_file
    first = (os.stat(out_file.name).st_size == 0)
    if first:
        # file = open(output_file, "")
        out_file.write("[Script Info]\n")
        out_file.write("; Script generated by " + NAME + " " + VERSION + "\n")
        out_file.write("; 9voltfansubs.wordpress.com\n")
        out_file.write("Title: SvgAssConvert Generated ASS File\n")
        out_file.write("ScriptType: v4.00+\n")
        out_file.write("WrapStyle: 0\n")
        out_file.write("ScaledBorderAndShadow: yes\n")
        out_file.write("YCbCr Matrix: None\n")
        out_file.write("\n")
        out_file.write("[Aegisub Project Garbage]\n")
        out_file.write("Active Line: 0\n")
        out_file.write("\n")
        out_file.write("[V4+ Styles]\n")
        out_file.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, " +
                       "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, " +
                       "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        out_file.write("Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000," +
                       "0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1\n")
        out_file.write("Style: SVG,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,10,10,10,1")
        out_file.write("\n")
        out_file.write("[Events]\n")
        out_file.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        # file.close()

# endregion


# region Helper functions

def parse_style(attribs):
    """
    Parse the style attributes
    :param attribs: Attributes; contains key "style" in format "stroke:#xxxxxx; fill:#xxxxxx;"
    :return: Fill, Stroke
    """
    fill = None
    stroke = None
    style = ""

    if "style" in attribs:
        style = attribs.get("style")

        style = style.replace(";", "")
        style = style.replace("#", "")
        styles = style.split(" ")
        if styles[0] == "stroke:":
            stroke = styles[1]
            fill = styles[3]
        elif styles[0] == "fill:":
            fill = styles[1]
            stroke = styles[3]
        else:
            for s in styles:
                if s.startswith("stroke:"):
                        stroke = s[7:]
                elif s.startswith("fill:"):
                        fill = s[5:]

    if fill is None or fill == "none":
        fill = "FFFFFF\\a&HFFF"
    if stroke is None or stroke == "none":
        stroke = "000000&\\3a&HFF"

    # Swap RGB to BGR
    if "\\a&" not in fill:
        chars = list(fill)
        # R R G G B B
        r1 = chars[0]
        r2 = chars[1]
        b1 = chars[4]
        b2 = chars[5]
        chars[0] = b1
        chars[1] = b2
        chars[4] = r1
        chars[5] = r2
        # B B G G R R
        fill = ''.join(chars)
    if "\\a&" not in stroke:
        chars = list(stroke)
        # R R G G B B
        r1 = chars[0]
        r2 = chars[1]
        b1 = chars[4]
        b2 = chars[5]
        chars[0] = b1
        chars[1] = b2
        chars[4] = r1
        chars[5] = r2
        # B B G G R R
        stroke = ''.join(chars)

    return fill, stroke


def strsum(*args):
    """
    Adds String representations of integers together
    ex "5" + "2" --> "7"
    :param args: Strings to be "added"
    :return: The integer result as a string
    """
    result = 0
    for i in range(0, len(args)):
        x = args[i]
        result += int(x)
    return str(result)


def strsub(*args):
    """
    Subtracts String representations of integers together
    ex "5" - "2" --> "3"
    :param args: Strings to be "subtracted"
    :return: The integer result as a string
    """
    result = int(args[0])
    for i in range(1, len(args)):
        x = args[i]
        result -= int(x)
    return str(result)


def strmul(*args):
    """
    Multiplies String representations of integers together
    ex "5" * "2" --> "10"
    :param args: Strings to be "multiplied"
    :return: The integer result as a string
    """
    result = 0
    for i in range(0, len(args)):
        x = args[i]
        result *= int(x)
    return str(result)

# endregion


def disp_help():
    """
    Displays help
    :return:
    """
    print(NAME + "v" + VERSION + ", by 9volt")
    print()
    print("Help:")
    print("Usage: " + NAME + " input.svg output.ass")
    print("input.svg: vector SVG to convert to .ass subtitle format")
    print("output.ass: Advanced SubStation Alpha subtitle file to export to.")
    print("  If the file does not exist, a new one will be created with the name given.")
    print("  If the file exists, lines will be appended to the end of the file.")
    print()
    print("Flags:")
    print("--verbose-output")
    print("  Prints each line being added in real-time")
    print("--force-new-file")
    print("  Will force the creation of a new file, even if the file already exists.")
    print("  (WILL DELETE ALL EXISTING CONTENTS)")


def main():
    """
    Run the program.
    Requires 2 additional command-line arguments:
        1) Path to input SVG file
        2) Path to output ASS file
    :return: None
    """
    if len(sys.argv) < 2:
        print("Usage:", NAME, "input.svg output.ass")
        sys.exit()
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        if sys.argv[1] == "help":
            disp_help()
        else:
            print("Usage:", NAME, "input.svg output.ass")
        sys.exit()

    global input_file
    global output_file
    global out_file
    global VERBOSE
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    opened = False

    if len(sys.argv) > 4:
        for i in range(3, len(sys.argv) - 1):
            if sys.argv[i] == "--verbose-output":
                VERBOSE = True
            if sys.argv[i] == "--force-new-file":
                out_file = open(output_file, "w").close()  # clear file
                out_file = open(output_file, "a")  # append
                opened = True
            else:
                out_file = open(output_file, "a")  # append
                opened = True

    if not opened:
        out_file = open(output_file, "a")  # append by default

    generate_file()
    read_input()

    # clean up
    out_file.close()


# Run the main function
if __name__ == "__main__":
    main()
