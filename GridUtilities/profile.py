import struct
from typing import Dict, Optional, Set, Tuple


class ProfileException(Exception):
    pass


class Profile:
    __NAME_TO_CALLSIGN: Dict[Optional[str], int] = {
        None: 65535,
        "AARON": 0,
        "ADAM": 1,
        "ADRIANA": 2,
        "ALAN": 3,
        "ALBERT": 177,
        "ALEJANDRO": 4,
        "ALEX": 5,
        "AMANDA": 216,
        "AMBER": 217,
        "AMY": 218,
        "ANAMARIA": 10,
        "ANASTASIA": 6,
        "ANDRE": 7,
        "ANDY": 8,
        "ANGEL": 178,
        "ANGELITO": 179,
        "ANN": 9,
        "ANTHONY": 11,
        "ARTHUR": 12,
        "ASHLEY": 219,
        "ASTRO": 13,
        "AUSTIN": 180,
        "BEN": 14,
        "BETTY": 15,
        "BILL": 16,
        "BILLY": 17,
        "BLAKE": 18,
        "BOB": 19,
        "BOOMER": 238,
        "BRAD": 20,
        "BRANDON": 21,
        "BRETT": 22,
        "BRIAN": 23,
        "BRITTNEY": 220,
        "BRUCE": 24,
        "BUBBA": 25,
        "BUTCH": 26,
        "CAITLIN": 27,
        "CALEB": 28,
        "CALVIN": 181,
        "CAMERON": 29,
        "CARL": 30,
        "CARLOS": 31,
        "CAROL": 32,
        "CARRIE": 221,
        "CHAD": 33,
        "CHARLES": 34,
        "CHARLIE": 35,
        "CHIP": 36,
        "CHRIS": 37,
        "CHRISTINA": 222,
        "CHUBBY": 239,
        "CLAYTON": 38,
        "CODY": 39,
        "COLIN": 40,
        "COREY": 41,
        "CRAIG": 42,
        "CRISPY": 241,
        "CURTIS": 182,
        "DAN": 43,
        "DARREL": 183,
        "DARRIN": 184,
        "DAVE": 44,
        "DAVID": 45,
        "DENNIS": 185,
        "DEREK": 186,
        "DONALD": 46,
        "DOUGLAS": 47,
        "DREW": 187,
        "DUDE": 48,
        "DUSTIN": 188,
        "DYLAN": 189,
        "ED": 49,
        "EDDIE": 50,
        "EDIE": 51,
        "EL HOMBRE": 242,
        "ELIAN": 52,
        "ELIZABETH": 53,
        "ENRIQUE": 54,
        "ERIC": 55,
        "EUGENE": 56,
        "EVAN": 57,
        "EVERYONE": 243,
        "FEMALE": 58,
        "FERNANDO": 59,
        "FLASH": 244,
        "FRANK": 60,
        "FRANK STEIN": 245,
        "GARRET": 190,
        "GARY": 61,
        "GENE": 62,
        "GEORGE": 63,
        "GERALD": 64,
        "GODZILLA": 246,
        "GRAHAM": 65,
        "GRAMPA": 247,
        "GRANT": 66,
        "GREG": 67,
        "GUS": 68,
        "HEATHER": 223,
        "HECTOR": 69,
        "HENRY": 70,
        "HERMAN": 71,
        "IAN": 72,
        "ICEMAN": 248,
        "ISAAC": 73,
        "ISABEL": 74,
        "IT": 75,
        "JACK": 76,
        "JACOB": 77,
        "JAIME": 191,
        "JAKE": 78,
        "JAMES": 79,
        "JAMIE": 80,
        "JARED": 192,
        "JASON": 81,
        "JAVIER": 82,
        "JAY": 83,
        "JEFF": 84,
        "JENNIFER": 85,
        "JENNY": 86,
        "JEREMY": 87,
        "JERRY": 88,
        "JESSICA": 224,
        "JIM": 89,
        "JIMMY": 90,
        "JOE": 91,
        "JOEL": 92,
        "JOHN": 93,
        "JORDAN": 96,
        "JOSE": 94,
        "JOSH": 95,
        "JUAN": 235,
        "JUSTIN": 97,
        "KEITH": 98,
        "KEN": 99,
        "KERRY": 100,
        "KEVIN": 101,
        "KIMBERLY": 225,
        "KURT": 102,
        "KYLE": 103,
        "LANCE": 193,
        "LARRY": 104,
        "LAUREN": 226,
        "LEE": 194,
        "LESLIE": 105,
        "LIZ": 106,
        "LOGAN": 195,
        "LOUIS": 107,
        "LUCAS": 196,
        "LUCIA": 108,
        "LUCRETIA": 109,
        "LUKE": 110,
        "MANUEL": 111,
        "MARIO": 197,
        "MARK": 112,
        "MARTIN": 113,
        "MARTY": 114,
        "MARY": 115,
        "MASTER": 251,
        "MATT": 116,
        "MATTHEW": 117,
        "MAURICE": 118,
        "MEGAN": 227,
        "MELISSA": 228,
        "MICHELLE": 229,
        "MIGUEL": 119,
        "MIKE": 120,
        "MIRIAM": 121,
        "MOUSE": 250,
        "NATHAN": 122,
        "NICHOLAS": 123,
        "NICK": 124,
        "NICO": 236,
        "NICOLE": 230,
        "NIGEL": 125,
        "NOBODY": 252,
        "OLD MAN": 253,
        "ORSMAB": 127,
        "OSCAR": 126,
        "PAT": 128,
        "PATRICK": 129,
        "PAUL": 130,
        "PAULO": 131,
        "PEDRO": 132,
        "PETER": 133,
        "PHAT": 254,
        "PRESIDENT": 255,
        "RACHEL": 231,
        "RAFAEL": 201,
        "RALPH": 198,
        "RAMALIS": 202,
        "RANDALL": 203,
        "RAPTOR": 258,
        "RAUL": 199,
        "RAYMOND": 200,
        "RHONDA": 136,
        "RICH": 134,
        "RICHARD": 135,
        "RICKY": 204,
        "ROB": 137,
        "ROBERT": 138,
        "ROCKY": 257,
        "ROGER": 205,
        "RONALD": 206,
        "ROSALIND": 237,
        "ROSS": 207,
        "ROY": 208,
        "RUBEN": 209,
        "RYAN": 139,
        "SAL": 140,
        "SAM": 210,
        "SARA": 232,
        "SASQUATCH": 265,
        "SCOOBY": 259,
        "SCORPION": 141,
        "SCOTT": 142,
        "SEAN": 143,
        "SERGIO": 144,
        "SHANE": 145,
        "SHAWN": 146,
        "SHE": 147,
        "SHERIDAN": 148,
        "SIMON": 211,
        "SKINNY": 260,
        "SLICK": 149,
        "SLIM": 261,
        "SLY": 262,
        "SOMEBODY": 263,
        "SPARKY": 150,
        "SPENCER": 151,
        "STACEY": 152,
        "STACY": 153,
        "STEVE": 154,
        "STUBBY": 266,
        "SUBZERO": 155,
        "SUPER FLY": 264,
        "SUSAN": 156,
        "SUZIE": 157,
        "STEPHANY": 233,
        "TAYLOR": 158,
        "TED": 159,
        "TERRY": 160,
        "THAT GIRL": 161,
        "THE CHIEF": 240,
        "THE GIRL": 162,
        "THE KID": 163,
        "THE KING": 249,
        "THE QUEEN": 256,
        "TIFFANY": 234,
        "TIGER": 164,
        "TIM": 165,
        "TITANIC": 267,
        "TODD": 166,
        "TOM": 167,
        "TONY": 168,
        "TRAVIS": 169,
        "TREVOR": 212,
        "TYLER": 170,
        "VICTOR": 213,
        "VINCE": 171,
        "WALTER": 172,
        "WAYNE": 173,
        "WESLEY": 214,
        "WILLIAM": 174,
        "WILLY": 215,
        "WILMA": 175,
        "WIZ": 268,
        "ZACH": 176,
    }

    def __init__(self, data: bytes) -> None:
        if len(data) != 86:
            raise Exception("Invalid profile length!")
        self.data: bytes = data
        self.callsigns: Set[str] = {k for k in self.__NAME_TO_CALLSIGN if k is not None}
        self.__call_lut: Dict[int, Optional[str]] = {v: k for k, v in self.__NAME_TO_CALLSIGN.items()}

        # There is a single byte in position 23 that the game always writes
        # a 0 to. This used to be a profile 'in use' flag but the game no
        # longer makes use of it. Also, there are 44 bytes of zeros between
        # the last valid byte in the profile and the checksum, which the game
        # does not touch when reading/writing profiles. These are not mapped
        # to any properties below.

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
        # Ensure data bit is set properly. If we edit an empty profile that
        # came from a reset chip this can be cleared.
        self.data = self.data[:31] + b"\x01" + self.data[32:]
        if len(self.data) != 86:
            raise Exception("Logic error! Somehow changed the data length!")
        new_checksum = self._calc_checksum()
        self.data = self.data[:-4] + struct.pack(">I", new_checksum)

    def clear(self) -> None:
        self.data = b"\xff" * 5 + b"\x00" * 26 + b"\x01" + b"\x00" * 54
        self._update_checksum()

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
            if char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ":
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
    def callsign(self) -> Optional[str]:
        if not self.valid:
            return None

        voicelow = struct.unpack(">B", self.data[13:14])[0]
        voicehigh = struct.unpack(">B", self.data[36:37])[0]

        callsign = (voicehigh << 8) | voicelow
        if callsign in self.__call_lut:
            return self.__call_lut[callsign]
        else:
            return None

    @callsign.setter
    def callsign(self, callsign: Optional[str]) -> None:
        if callsign not in self.__NAME_TO_CALLSIGN:
            raise ProfileException("Not a valid callsign!")
        callint = self.__NAME_TO_CALLSIGN[callsign]

        self.data = (
            self.data[:13] +
            struct.pack(">B", callint & 0xFF) +
            self.data[14:36] +
            struct.pack(">B", (callint >> 8) & 0xFF) +
            self.data[37:]
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
        if tower < 1 or tower > 9:
            raise ProfileException("Invalid tower value")
        posbyte = (((tower - 1) & 0xF) << 4) | ((level - 1) & 0xF)
        self.data = (
            self.data[:34] +
            struct.pack(">B", posbyte) +
            self.data[35:]
        )
        self._update_checksum()

    @property
    def towerclears(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">B", self.data[35:36])[0]

    @towerclears.setter
    def towerclears(self, clears: int) -> None:
        self.data = self.data[:35] + struct.pack(">B", clears) + self.data[36:]
        self._update_checksum()

    def _get_control_settings(self) -> int:
        if not self.valid:
            return 0

        return struct.unpack(">B", self.data[30:31])[0]

    def _set_control_settings(self, settings: int) -> None:
        self.data = (
            self.data[:30] +
            struct.pack(">B", settings) +
            self.data[31:]
        )
        self._update_checksum()

    @property
    def freelook(self) -> bool:
        return (self._get_control_settings() & 0x02) != 0

    @freelook.setter
    def freelook(self, enabled: bool) -> None:
        if enabled:
            # Make sure to enable it
            self._set_control_settings(self._get_control_settings() | 0x02)
        else:
            # Reverse aim requires free look
            self._set_control_settings(0x00)

    @property
    def invertaim(self) -> bool:
        return self.freelook and ((self._get_control_settings() & 0x01) != 0)

    @invertaim.setter
    def invertaim(self, enabled: bool) -> None:
        if self.freelook:
            # Only apply if free look is enabled
            if enabled:
                # Make sure to enable it
                self._set_control_settings(self._get_control_settings() | 0x01)
            else:
                # Disable it!
                self._set_control_settings(self._get_control_settings() & 0xFE)

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

        def format_controls(freelook: bool, invertaim: bool) -> str:
            if freelook:
                if invertaim:
                    return "free look + inverted"
                else:
                    return "free look"
            else:
                return "assist"

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
                if self.totalplays > 0 else '0%',
            ),
            line("Total Points", self.totalpoints),
            line("Longest Streak", self.streak),
            line("High Score", self.highscore),
            line("Total Cash", format_cash(self.totalcash)),
            line("Tower Progress", format_tower(self.towerposition)),
            line("Tower Clears", self.towerclears),
            line(
                "Control Mode",
                format_controls(self.freelook, self.invertaim),
            )
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
        self._profiles[key].clear()

    def __iter__(self):
        return iter(self._profiles)

    def __reversed__(self):
        return reversed(self._profiles)
