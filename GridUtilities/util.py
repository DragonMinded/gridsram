#! /usr/bin/env python3
import argparse


class ByteUtil:

    @staticmethod
    def byteswap(data: bytes) -> bytes:
        even = [d for d in data[::2]]
        odd = [d for d in data[1::2]]
        chunks = [bytes([odd[i], even[i]]) for i in range(len(even))]
        return b''.join(chunks)

    @staticmethod
    def wordswap(data: bytes) -> bytes:
        one = [d for d in data[::4]]
        two = [d for d in data[1::4]]
        three = [d for d in data[2::4]]
        four = [d for d in data[3::4]]
        chunks = [
            bytes([four[i], three[i], two[i], one[i]])
            for i in range(len(one))
        ]
        return b''.join(chunks)

    @staticmethod
    def combine16bithalves(upper: bytes, lower: bytes) -> bytes:
        chunks = [
            b''.join([upper[i:(i+2)], lower[i:(i+2)]])
            for i in range(0, len(upper), 2)
        ]
        return b''.join(chunks)

    @staticmethod
    def combine8bithalves(upper: bytes, lower: bytes) -> bytes:
        chunks = [bytes([upper[i], lower[i]]) for i in range(len(upper))]
        return b''.join(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("ROM manipulation utilities.")
    subparsers = parser.add_subparsers(
        dest="action",
        help="Action to perform.",
    )

    combine16 = subparsers.add_parser(
        "combine16",
        help="Combine two 16bit roms to one 32bit rom.",
    )
    combine16.add_argument(
        "upper",
        metavar="UPPER",
        type=str,
        help="Upper half of rom file.",
    )
    combine16.add_argument(
        "lower",
        metavar="LOWER",
        type=str,
        help="Lower half of rom file.",
    )
    combine16.add_argument(
        "combined",
        metavar="COMBINED",
        type=str,
        help="Combined output file.",
    )

    args = parser.parse_args()
    if args.action == "combine16":
        with open(args.upper, "rb") as fp:
            upper = fp.read()
        with open(args.lower, "rb") as fp:
            lower = fp.read()
        with open(args.combined, "wb") as fp:
            fp.write(ByteUtil.combine16bithalves(upper, lower))
    else:
        raise Exception("Unrecognized command!")
