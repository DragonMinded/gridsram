#! /usr/bin/env python3
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Convert a cabinet SRAM dump to a format compatible for use in MAME."
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
        if len(data) != 0x20000:
            raise Exception("Input file is not the correct length!")

        with open(args.outfile, "wb") as ofp:
            ofp.write(b"".join(bytes([b, 0, 0, 0]) for b in data))

    print(f"Wrote MAME-compatible SRAM file to {args.outfile}")
