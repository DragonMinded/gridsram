import struct
import sys


class ProfileException(Exception):
    pass


class Profile:

    def __init__(self, data: bytes) -> None:
        if len(data) != 86:
            raise Exception("Invalid profile length!")
        self.data = data

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

    @property
    def valid(self) -> bool:
        stored_checksum = struct.unpack(">I", self.data[-4:])[0]
        if stored_checksum != self._calc_checksum():
            return False
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
        if len(newname) < 1 or len(newname) > 8:
            raise ProfileException("Invalid name length!")
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

        # TODO: This might not be the correct offset
        voicelow, voicehigh = struct.unpack(">BB", self.data[13:15])

        # TODO: LUT for this
        return str((voicehigh << 8) | voicelow)

    @property
    def age(self) -> int:
        if not self.valid:
            return 0

        # TODO: This is the wrong offset
        return struct.unpack(">I", self.data[16:20])[0]

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
    def totalplays(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">H", self.data[32:34])[0]

    @totalplays.setter
    def totalplays(self, plays: int) -> None:
        self.data = self.data[:32] + struct.pack(">H", plays) + self.data[34:]
        self._update_checksum()


def print_profile(profile: Profile, *, print_failures) -> None:
    if profile.valid:
        print("Pin code", profile.pin)
        print("Name", profile.name)
        print("Call Sign", profile.callsign)
        print("Games Played", profile.totalplays)
        print("Total Points", profile.totalpoints)
        print("Longest Streak", profile.streak)
        print("High Score", profile.highscore)
        print("Total Cash", profile.totalcash)
    elif print_failures:
        print("Invalid profile")


def read_profile(chunk, spot, *, print_failures) -> None:
    profile = Profile(chunk[(86 * spot):][:86])
    print_profile(profile, print_failures=print_failures)


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fp:
        data = fp.read()

    try:
        read_profile(data, int(sys.argv[2]), print_failures=True)
    except IndexError:
        for spot in range(0, 1524):
            read_profile(data, spot, print_failures=False)
