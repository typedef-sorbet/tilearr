from sys import argv, exit
from os.path import isfile
import argparse

parser = argparse.ArgumentParser(
    prog="tilearr",
    description="Formats output(s) of rgbgfx as a .c file that GBDK can use",
)

parser.add_argument("-d", "--tiledata", default="", help="Color data for each tile. This should be the default output file of rgbgfx.")
parser.add_argument("-t", "--tilemap", default="", help="Tile mapping data. This should be the same as what was output for rgbgfx's -t/-T flag.")
parser.add_argument("-p", "--palette", default="", help="Palette mapping data. This should be the same as what was output for rgbgfx's -p/-P flag.")
parser.add_argument("-a", "--attrmap", default="", help="Tile mapping data. This should be the same as what was output for rgbgfx's -a/-A flag.")
parser.add_argument("-n", "--name", default="image", help="What you want each C array to be prefixed with in the resulting .c file.")
parser.add_argument("-o", "--output", default="image.c", help="Output file, structured as a C source file.")

args = parser.parse_args()

valid = True

for file, descriptor in [(args.tiledata, "Tile data"), 
                        (args.tilemap, "Tile map"), 
                        (args.palette, "Palette"), 
                        (args.attrmap, "Attribute map")]:
    if file != "" and not isfile(file):
        print(f"Error: {descriptor} file {file} does not exist.")
    valid = valid and (file == "" or isfile(file))

if not valid:
    exit(1)

with open(args.output, mode='w') as outfile:
    outfile.write("#include <gb/gb.h>\n")

    # Raw tile data
    if args.tiledata and isfile(args.tiledata):
        with open(args.tiledata, mode='rb') as tiledata_file:
            tiledata = tiledata_file.read()

        outfile.write(f"const UINT16 {args.name}_tileCount = {len(tiledata) // 16};\n")
        outfile.write(f"const unsigned char {args.name}_tileData[] = {{\n")
        for tile_num in range(len(tiledata) // 16):
            offset = tile_num * 16
            this_tile = tiledata[offset:offset+16]
            tiles_as_hex = ",".join(
                map(lambda _tile: "0x{:02X}".format(_tile), this_tile)
            )
            outfile.write(f"/* Tile {tile_num} */ {tiles_as_hex},\n")
        outfile.write("};\n")

    # Tilemap (mapping each tile to an 8x8 space on the screen)
    if args.tilemap and isfile(args.tilemap):
        with open(args.tilemap, mode='rb') as tilemap_file:
            tilemap_data = tilemap_file.read()

        outfile.write(f"const unsigned char {args.name}_tileMapData[] = {{\n")

        for tilemap_num in range(len(tilemap_data) // 16):
            offset = tilemap_num * 16
            this_mapping = tilemap_data[offset : offset + 16]
            mapping_as_hex = ",".join(
                map(lambda t: "0x{:02X}".format(t), this_mapping)
            )
            outfile.write(f"\t{mapping_as_hex},\n")
        outfile.write("};\n")

    # Attrmap (assigning attributes to each 8x8 space on the screen, e.g. flip, palette index, etc.)
    if args.attrmap and isfile(args.attrmap):
        with open(args.attrmap, mode='rb') as attrmap_file:
            attrmap_data = attrmap_file.read()

        outfile.write(f"const unsigned char {args.name}_attrMapData[] = {{\n")

        for attr_num in range(len(attrmap_data) // 16):
            offset = attr_num * 16
            this_attr = attrmap_data[offset : offset + 16]
            attr_as_hex = ",".join(
                map(lambda a: "0x{:02X}".format(a), this_attr)
            )
            outfile.write(f"\t{attr_as_hex},\n")
        outfile.write("};\n")

    # Palette
    if args.palette and isfile(args.palette):
        with open(args.palette, mode='rb') as palette_file:
            palette_data = palette_file.read()

        outfile.write(f"const UWORD {args.name}_palette[{len(palette_data) // 2}] = {{\n")

        # This one is a little different.
        # Pull out palette data 2 bytes at a time, and swap the endianness.
        for palette_num in range(len(palette_data) // 2):
            offset = palette_num * 2
            this_palette = palette_data[offset:offset+2]
            palette_endian_swapped = "0x{:02X}{:02X}".format(this_palette[1], this_palette[0])
            outfile.write(palette_endian_swapped + ",\n")
        outfile.write("};\n")
