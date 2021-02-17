from typing import Union


class ByteArray:
    def __init__(self, packet: Union[bytes, int, str] = b""):
        self.packet: bytes = b""

        if len(packet) > 0:
            self.write(packet)
            
    def copy(self):
        return ByteArray(self.packet)

    def read(self, length: int):
        value = b""
        if length <= len(self):
            value = self.get()[:length]
            self.packet = self.get()[length:]
        return value

    def read_bool(self) -> bool:
        return bool(self.read_byte())

    def read_byte(self) -> int:
        return int.from_bytes(self.read(1), "big")

    def read_short(self) -> int:
        return int.from_bytes(self.read(2), "big")

    def read_int(self) -> int:
        return int.from_bytes(self.read(4), "big")

    def read_utf(self) -> str:
        return self.read(self.read_short()).decode("ISO-8859-1")

    def write(self, value: Union[bytes, int, str]):
        if isinstance(value, int):
            value = chr(value).encode("ISO-8859-1")
        elif isinstance(value, str):
            value = value.encode("ISO-8859-1")
        self.packet += value
        return self

    def write_bool(self, value: bool):
        self.write_byte(int(value))
        return self

    def write_byte(self, value: int):
        self.write(value.to_bytes(1, "big"))
        return self

    def write_short(self, value: int):
        self.write(value.to_bytes(2, "big"))
        return self

    def write_int(self, value: int):
        self.write(value.to_bytes(4, "big"))
        return self

    def write_utf(self, value: str):
        self.write_short(len(value)).write(value)
        return self

    def get(self):
        return self.packet

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.get().decode("ISO-8859-1")

    def __len__(self):
        return len(self.get())
