#! /usr/bin/env python3
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Convert a MAME SRAM file to a format compatible for use on a cabinet."
    )
    parser.add_argument(
        "infile",
        metavar="INFILE",
        type=str,
        help="File to load for conversion",
    )
    parser.add_argument(
        "outfile",
        metavar="OUTFILE",
        type=str,
        help="File to write after conversion",
    )
    args = parser.parse_args()
    with open(args.infile, "rb") as ifp:
        data = ifp.read()
        if len(data) != 0x80000:
            raise Exception("Input file is not the correct length!")

        with open(args.outfile, "wb") as ofp:
            ofp.write(data[::4])

    print(f"Wrote cabinet-compatible SRAM file to {args.outfile}")
