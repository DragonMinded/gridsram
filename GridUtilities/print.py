#! /usr/bin/env python3
import argparse
from profile import Profile, TowerClear, SRAM


def print_profile(profile: Profile) -> None:
    if profile.valid:
        print(str(profile), "\n")
    else:
        print("Invalid profile", "\n")


def print_tower(tower: TowerClear) -> None:
    print(str(tower), "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Print utility to display The Grid SRAM profiles and tower completion times.",
    )
    parser.add_argument(
        'file',
        metavar="FILE",
        type=str,
        help="SRAM file to parse and print.",
    )
    parser.add_argument(
        "--offset",
        type=str,
        default=None,
        help="Profile offset index. If omitted all profiles and towers will be printed.",
    )
    parser.add_argument(
        "--mame-compat",
        action="store_true",
        help="SRAM file is from MAME instead of a dump.",
    )
    args = parser.parse_args()
    if args.offset is None:
        offset = None
    elif args.offset[:2] == "0x":
        offset = int(args.offset[2:], 16)
    else:
        offset = int(args.offset)

    with open(args.file, 'rb') as fp:
        data = fp.read()
    sram = SRAM(data, is_mame_format=args.mame_compat)

    if offset is None:
        for index, profile in enumerate(sram.profiles):
            if profile.valid:
                print("Offset index", index)
                print_profile(profile)

        for index, clear in enumerate(sram.towers):
            tower = int(index / 6)
            level = index % 6
            print(f"Tower {tower + 1}, {level + 1}")
            print_tower(clear)
    else:
        print_profile(sram.profiles[offset])
