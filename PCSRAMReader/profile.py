import struct
from typing import Tuple


class ProfileException(Exception):
    pass


class Profile:
    def __init__(self, data: bytes) -> None:
        if len(data) != 86:
            raise Exception("Invalid profile length!")
        self.data = data

        # There's a couple fields missing here, but it looks like in
        # practice they are always 0x00 so it doesn't matter particularly
        # much. The top byte for voice calls is missing, but as detailed
        # below, it might not matter. The 'in use' flag is also somewhere
        # but the game does not use it any longer, so its always set to 0x00.
        # Similar thing goes for control mod and towers complete (looks
        # to be redundant with tower position). Each of these missing fields
        # is 1 byte, and there are 4 holes unaccounted for in the data, so
        # these values go to offsets 23, 30, 35 and 36 (not respectively).

    def _calc_checksum(self) -> int:
        rotatebit = 1
        checksum = 0
        for val in self.data[:-4]:
            val = (val | rotatebit) & 0xFF

            rotatebit = rotatebit << 1
            if rotatebit == 256:
                rotatebit = 1

            checksum = checksum + val

        return checksum

    def _update_checksum(self) -> None:
        new_checksum = self._calc_checksum()
        self.data = self.data[:-4] + struct.pack(">I", new_checksum)

    @classmethod
    def create(cls) -> "Profile":
        return Profile(b"\xff" * 5 + b"\x00" * 26 + b"\x01" +b"\x00" * 54)

    @property
    def valid(self) -> bool:
        # First, validate checksum
        stored_checksum = struct.unpack(">I", self.data[-4:])[0]
        if stored_checksum != self._calc_checksum():
            return False

        # Next, verify the data version
        if self.data[31] != 0x01:
            return False

        # Finally, return as long as we aren't setting the pin to unused
        return self.data[0:5] != b"\xff\xff\xff\xff\xff"

    @property
    def pin(self) -> str:
        if not self.valid:
            return ""

        length, pin = struct.unpack(">BI", self.data[0:5])
        pin = pin | ((length & 0x0F) << 32)
        length = (length >> 4) & 0x0F

        pin = str(pin)
        while len(pin) < length:
            pin = "0" + pin
        return pin

    @pin.setter
    def pin(self, code: str) -> None:
        if len(code) < 5 or len(code) > 10:
            raise ProfileException("Invalid pin code length!")
        if not code.isdigit():
            raise ProfileException("Non-digit pin code provided!")

        intcode = int(code)
        length = ((len(code) << 4) & 0xF0) | ((intcode >> 32) & 0x0F)
        rest = intcode & 0xFFFFFFFF

        self.data = struct.pack(">BI", length, rest) + self.data[5:]
        self._update_checksum()

    @property
    def name(self) -> str:
        if not self.valid:
            return ""

        vals = struct.unpack(">ssssssss", self.data[5:13])
        namestr = (
            vals[3] + vals[2] + vals[1] + vals[0] +
            vals[7] + vals[6] + vals[5] + vals[4]
        )
        return namestr.rstrip(b"\0").decode('ascii')

    @name.setter
    def name(self, newname: str) -> None:
        if len(newname) < 1 or len(newname) > 7:
            raise ProfileException("Invalid name length!")
        for char in newname:
            if char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ ":
                raise ProfileException("Invalid name character!")
        namebytes = newname.encode('ascii')
        while len(namebytes) < 8:
            namebytes = namebytes + b"\0"

        self.data = (
            self.data[:5] +
            bytes([
                namebytes[3],
                namebytes[2],
                namebytes[1],
                namebytes[0],
                namebytes[7],
                namebytes[6],
                namebytes[5],
                namebytes[4],
            ]) +
            self.data[13:]
        )
        self._update_checksum()

    @property
    def callsign(self) -> str:
        if not self.valid:
            return ""

        # TODO: Missing top half of the offset, but it might be fine
        # if the game doesn't have > 256 voices.
        voicelow = struct.unpack(">B", self.data[13:14])[0]
        voicehigh = 0

        # TODO: LUT for this
        return str((voicehigh << 8) | voicelow)

    @callsign.setter
    def callsign(self, callsign: int) -> None:
        self.data = (
            self.data[:13] +
            struct.pack(">B", callsign) +
            self.data[14:]
        )
        self._update_checksum()

    @property
    def age(self) -> int:
        if not self.valid:
            return 0

        # No setter for this, it doesn't make sense.
        return struct.unpack(">I", self.data[15:19])[0]

    @property
    def highscore(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">B", self.data[14:15])[0]

    @highscore.setter
    def highscore(self, score: int) -> None:
        self.data = self.data[:14] + struct.pack(">B", score) + self.data[15:]
        self._update_checksum()

    @property
    def streak(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">B", self.data[37:38])[0]

    @streak.setter
    def streak(self, streak: int) -> None:
        self.data = self.data[:37] + struct.pack(">B", streak) + self.data[38:]
        self._update_checksum()

    @property
    def totalpoints(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">I", self.data[19:23])[0]

    @totalpoints.setter
    def totalpoints(self, points: int) -> None:
        self.data = self.data[:19] + struct.pack(">I", points) + self.data[23:]
        self._update_checksum()

    @property
    def totalcash(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">I", self.data[26:30])[0]

    @totalcash.setter
    def totalcash(self, cash: int) -> None:
        self.data = self.data[:26] + struct.pack(">I", cash) + self.data[30:]
        self._update_checksum()

    @property
    def totalwins(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">H", self.data[24:26])[0]

    @totalwins.setter
    def totalwins(self, wins: int) -> None:
        self.data = self.data[:24] + struct.pack(">H", wins) + self.data[26:]
        self._update_checksum()

    @property
    def totalplays(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">H", self.data[32:34])[0]

    @totalplays.setter
    def totalplays(self, plays: int) -> None:
        self.data = self.data[:32] + struct.pack(">H", plays) + self.data[34:]
        self._update_checksum()

    @property
    def towerposition(self) -> Tuple[int, int]:
        if not self.valid:
            return (1, 1)

        posbyte = struct.unpack(">B", self.data[34:35])[0]
        tower = ((posbyte >> 4) & 0xF) + 1
        level = (posbyte & 0xF) + 1
        return (tower, level)

    @towerposition.setter
    def towerposition(self, towerposition: Tuple[int, int]) -> None:
        tower, level = towerposition
        if level < 1 or level > 6:
            raise ProfileException("Invalid level value")
        if tower < 1 or tower > 6:
            # I think this is the upper bound?
            raise ProfileException("Invalid tower value")
        posbyte = (((tower - 1) & 0xF) << 4) | ((level - 1) & 0xF)
        self.data = (
            self.data[:34] +
            struct.pack(">B", posbyte) +
            self.data[35:]
        )
        self._update_checksum()

    def __str__(self) -> str:
        if not self.valid:
            raise ProfileException("Cannot render invalid profile!")

        def line(title: str, content: object) -> str:
            return title + ": " + str(content)

        def format_cash(cash: int) -> str:
            cashstr = '$' + str(cash)
            if cash >= 1000:
                # At least 1000 dollars, lets put a comma
                cashstr = cashstr[:-3] + "," + cashstr[-3:]
            return cashstr

        def format_tower(position: Tuple[int, int]) -> str:
            tower, level = position
            return "Tower " + str(tower) + ", Level " + str(level)

        return "\n".join([
            line("Name", self.name),
            line("Pin Code", self.pin),
            line("Call Sign", self.callsign),
            line("Age", self.age),
            line("Games Won", self.totalwins),
            line("Games Played", self.totalplays),
            line(
                "Win Percentage",
                str(int((self.totalwins * 100) / self.totalplays)) + '%'
                if self.totalplays > 0 else '0%'
            ),
            line("Total Points", self.totalpoints),
            line("Longest Streak", self.streak),
            line("High Score", self.highscore),
            line("Total Cash", format_cash(self.totalcash)),
            line("Tower Progress", format_tower(self.towerposition))
        ])


class ProfileCollection:
    def __init__(self, data: bytes, *, is_mame_format: bool = False) -> None:
        if is_mame_format:
            # Mame stores the SRAM for The Grid as 32-bit integers for each
            # 8-bit value in the SRAM. This is because the game maps the chip
            # to a 32-bit address with the top 24 bits zero'd out. So,
            # compensate for this.
            data = data[::4]
        if len(data) != 131072:
            raise ProfileException("Invalid profile chunk!")

        # Save this for serialization
        self._mame_compat = is_mame_format

        def read_profile(chunk: bytes, spot: int) -> Profile:
            return Profile(chunk[(86 * spot):][:86])

        self._profiles = [read_profile(data, spot) for spot in range(0, 1500)]
        self._extra = data[(1500 * 86):]

    @property
    def data(self) -> bytes:
        data = b"".join(p.data for p in self._profiles)
        data = data + self._extra
        if len(data) != 131072:
            raise Exception("Logic error, shouldn't be possible!")

        if self._mame_compat:
            # We need to convert back to make broken style here
            data = b"".join(bytes([b, 0, 0, 0]) for b in data)

        return data

    def __len__(self) -> int:
        return len(self._profiles)

    def __getitem__(self, key: int) -> Profile:
        return self._profiles[key]

    def __setitem__(self, key: int, value: object) -> None:
        if not isinstance(value, Profile):
            raise ProfileException(
                "Cannot assign non-Profile to ProfileCollection entry!"
            )
        self._profiles[key] = value

    def __delitem__(self, key: int) -> None:
        # Map this to erasing a profile
        self._profiles[key] = Profile.create()

    def __iter__(self):
        return iter(self._profiles)

    def __reversed__(self):
        return reversed(self._profiles)
