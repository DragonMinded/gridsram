import serial
import struct


class SRAMProtocol:

    CONTINUATION_RUN_READ = 1024
    CONTINUATION_RUN_WRITE = 32

    def __init__(self, port: str) -> None:
        ser = serial.Serial(
            port=port,
            baudrate=230400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )

        if not ser.isOpen():
            raise Exception("Could not open {port}!".format(port=port))
        ser.flushInput()
        ser.flushOutput()
        self.__serial = ser

        # Wait for arduino to come up
        while not self.__available():
            pass
        self.__serial.timeout = None

    def __available(self) -> bool:
        self.__serial.write(b'SRAMS')
        self.__serial.flush()
        try:
            self.__check_return()
            return True
        except Exception:
            return False

    def __check_return(self) -> None:
        resp = self.__serial.read(size=2)
        if resp == b'OK':
            return
        if resp != b'NG':
            raise Exception('Unexpected return from Arduino!')

        # Read error until we get null byte
        error = b''
        while True:
            val = self.__serial.read(size=1)
            if val == b'\00':
                raise Exception(error.decode('utf-8'))
            error = error + val

    def __check_continue(self) -> None:
        resp = b""
        while True:
            resp += self.__serial.read(size=2)
            if len(resp) < 2:
                continue
            if resp == b'CO':
                return
            if resp == b'NG':
                # Read error until we get null byte
                error = b''
                while True:
                    val = self.__serial.read(size=1)
                    if val == b'\00':
                        raise Exception(error.decode('utf-8'))
                    error = error + val

            # Unrecognized input
            raise Exception('Unexpected return from Arduino!')

    def write(self, address: int, data: bytes) -> None:
        start = address
        end = address + len(data)

        self.__serial.write(b'SRAMW')
        self.__serial.write(
            struct.pack(
                '@BBB',
                (start >> 16) & 0xFF,
                (start >> 8) & 0xFF,
                start & 0xFF,
            )
        )
        self.__serial.write(
            struct.pack(
                '@BBB',
                (end >> 16) & 0xFF,
                (end >> 8) & 0xFF,
                end & 0xFF,
            )
        )

        # Send in chunks
        while len(data) > 0:
            self.__check_continue()
            self.__serial.write(data[:self.CONTINUATION_RUN_WRITE])
            self.__serial.flush()
            data = data[self.CONTINUATION_RUN_WRITE:]

        self.__check_return()

    def read(self, address: int, length: int) -> bytes:
        start = address
        end = address + length

        self.__serial.write(b'SRAMR')
        self.__serial.write(
            struct.pack(
                '@BBB',
                (start >> 16) & 0xFF,
                (start >> 8) & 0xFF,
                start & 0xFF,
            )
        )
        self.__serial.write(
            struct.pack(
                '@BBB',
                (end >> 16) & 0xFF,
                (end >> 8) & 0xFF,
                end & 0xFF,
            )
        )
        self.__serial.flush()
        self.__check_continue()

        # Send in chunks
        data = b''
        while len(data) < length:
            self.__serial.write(b'CO')
            self.__serial.flush()
            data = data + self.__serial.read(size=min(self.CONTINUATION_RUN_READ, length - len(data)))

        self.__check_return()
        return data
