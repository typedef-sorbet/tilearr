from sys import argv
import argparse

parser = argparse.ArgumentParser(
    prog="tilemap2arr",
    description="Transforms output of rgbgfx to a .c file that GBDK can use",
)

parser.add_argument("-d", "--tiledata", required=True)
parser.add_argument("-t", "--tilemap", required=True)
parser.add_argument("-p", "--palette", required=True)
parser.add_argument("-a", "--attrmap", required=True)
parser.add_argument("-n", "--name", default="background")
parser.add_argument("-o", "--output", default="tilemap2arr.c")

args = parser.parse_args()

with (open(args.tiledata, mode='rb') as tiledata_file,
      open(args.tilemap, mode='rb') as tilemap_file,
      open(args.palette, mode='rb') as palette_file,
      open(args.attrmap, mode='rb') as attrmap_file,
      open(args.output, mode='w') as outfile):
    tilemap_data = tilemap_file.read()
    tiledata = tiledata_file.read()
    palette_data = palette_file.read()
    attrmap_data = attrmap_file.read()

    outfile.write("#include <gb/gb.h>\n")
    outfile.write(f"const UINT16 {args.name}_tileCount = {len(tiledata) // 16};")

    # Tile data

    outfile.write(f"const unsigned char {args.name}_tileData[] = {{\n")
    for tile_num in range(len(tiledata) // 16):
        offset = tile_num * 16
        this_tile = tiledata[offset:offset+16]
        tiles_as_hex = ",".join(
            map(lambda _tile: "0x{:02X}".format(_tile), this_tile)
        )
        outfile.write(f"/* Tile {tile_num} */ {tiles_as_hex},\n")
    outfile.write("};\n")

    # Tilemap

    outfile.write(f"const unsigned char {args.name}_tileMapData[] = {{\n")

    for tilemap_num in range(len(tilemap_data) // 16):
        offset = tilemap_num * 16
        this_mapping = tilemap_data[offset : offset + 16]
        mapping_as_hex = ",".join(
            map(lambda t: "0x{:02X}".format(t), this_mapping)
        )
        outfile.write(f"/* Mapping {tilemap_num} */ {mapping_as_hex},\n")
    outfile.write("};\n")

    # Attrmap

    outfile.write(f"const unsigned char {args.name}_attrMapData[] = {{\n")

    for attr_num in range(len(attrmap_data) // 16):
        offset = attr_num * 16
        this_attr = attrmap_data[offset : offset + 16]
        attr_as_hex = ",".join(
            map(lambda a: "0x{:02X}".format(a), this_attr)
        )
        outfile.write(f"/* Attr {attr_num} */ {attr_as_hex},\n")
    outfile.write("};\n")

    # Palette

    print(f"palette_data: {palette_data} (len {len(palette_data)})")

    outfile.write(f"const UWORD {args.name}_palette[{len(palette_data) // 2}] = {{\n")

    # This one is a little different.
    # Pull out palette data 2 bytes at a time, and swap the endianness.

    # Palette file ends in 0x0A, strip that off
    for palette_num in range(len(palette_data) // 2):
        offset = palette_num * 2
        this_palette = palette_data[offset:offset+2]
        palette_endian_swapped = "0x{:02X}{:02X}".format(this_palette[1], this_palette[0])
        outfile.write(palette_endian_swapped + ",\n")
    outfile.write("};\n")

# Original

# with open(argv[1], mode="rb") as tilemap_file:
#     with open(argv[1] + ".t2aout", mode="w") as outfile:
#         tilemap_data = tilemap_file.read()
#         outfile.write("#include <gb/gb.h>")
#         outfile.write(f"const UINT16 tileCount = {len(tilemap_data)};\n")
#         outfile.write("const unsigned char data = {\n")
#         for tile_num in range(len(tilemap_data) // 16):
#             offset = tile_num * 16
#             tile_data = tilemap_data[offset : offset + 16]
#             tiles_as_hex = ",".join(
#                 map(lambda _tile: "0x{:02X}".format(_tile), tile_data)
#             )
#             outfile.write(f"/* Tile {tile_num} */ {tiles_as_hex},\n")
#         outfile.write("};\n")
