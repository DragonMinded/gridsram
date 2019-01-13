import struct
import sys


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

    @property
    def valid(self) -> bool:
        stored_checksum = struct.unpack(">I", profile.data[-4:])[0]
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

    @property
    def callsign(self) -> str:
        if not self.valid:
            return ""

        voicelow, voicehigh = struct.unpack(">BB", self.data[13:15])

        # TODO: LUT for this
        return str((voicehigh << 8) | voicelow)

    @property
    def highscore(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">B", self.data[15:16])[0]

    @property
    def age(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">I", self.data[16:20])[0]


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fp:
        chunk = fp.read()

    spot = int(sys.argv[2])
    profile = Profile(chunk[(86 * spot):][:86])
    if profile.valid:
        print("Pin code", profile.pin)
        print("Name", profile.name)
        print("Call Sign", profile.callsign)
        print("High Score", profile.highscore)
        print("Profile Age", profile.age)
    else:
        print("Invalid profile")
