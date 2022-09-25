#! /usr/bin/env python3
import argparse
from proto import SRAMProtocol

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Dump utility to read/write SRAM.")
    parser.add_argument(
        "action",
        metavar="ACTION",
        type=str,
        help="Action to perform, such as 'read' or 'write'.",
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        type=str,
        help="File to perform action with.",
    )
    parser.add_argument(
        "--port",
        metavar="PORT",
        type=str,
        default="/dev/ttyACM0",
        help="Serial port of the helper Arduino. Defaults "
        + "to default Arduino port on Linux which is '/dev/ttyACM0'.",
    )
    parser.add_argument(
        "--offset",
        type=str,
        default="0",
        help="Offset address, defaults to beginning of chip.",
    )
    parser.add_argument(
        "--length",
        type=str,
        default="0x20000",
        help="Length of read action, defaults to size of chip.",
    )
    args = parser.parse_args()
    if args.offset[:2] == "0x":
        offset = int(args.offset[2:], 16)
    else:
        offset = int(args.offset)
    if args.length[:2] == "0x":
        length = int(args.length[2:], 16)
    else:
        length = int(args.length)

    sp = SRAMProtocol(args.port)
    if args.action == "read":
        data = sp.read(offset, length)
        with open(args.file, "wb") as fp:
            fp.write(data)
    elif args.action == "write":
        with open(args.file, "rb") as fp:
            data = fp.read()
        sp.write(offset, data)
    else:
        raise Exception("Unrecognized action!")
