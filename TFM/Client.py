import asyncio
import random

from .utils.ByteArray import ByteArray
from typing import List, Union


class Client(asyncio.Protocol):
    def __init__(self, server):
        # Instances
        self.packet: ByteArray = ByteArray()
        self.server: Server = server
        self.transport: asyncio.Transport = None

        # Bool
        self.is_closed: bool = False

        # Integer
        self.id: int = 0
        self.last_packet_id: int = random.randint(0, 99)

        # String
        self.name: str = ""
        self.ip_address: str = "0.0.0.0"

        # Loop
        self.loop = asyncio.get_running_loop()
        #super().__init__(server=self.server)
        
    def get_new_len(self, b: ByteArray):
        var_2068 = 0
        var_2053 = 0
        var_176 = b
        while var_2053 < 10:
            var_56 = var_176.read_byte() & 255
            var_2068 = var_2068 | (var_56 & 127) << 7 * var_2053
            var_2053 += 1
            if not ((var_56 & 128) == 128 and var_2053 < 5):
                return var_2068+1, var_2053

    def data_received(self, packet: bytes):
        if len(packet) < 2:
            return None

        if self.is_closed:
            return None

        if packet.startswith(b"<policy-file-request/>"):
            self.transport.write(
                b'<cross-domain-policy><allow-access-from domain="*" to-ports="*"/></cross-domain-policy>'
            )
            return self.transport.close()

        self.packet.write(packet)
        old_packet = self.packet.copy()
        while len(self.packet) > 0:
            length, lenlen = self.get_new_len(self.packet)
            if len(self.packet) >= length:
                read = ByteArray(self.packet.get()[:length])
                old_packet.packet = old_packet.get()[length:]
                self.packet.packet = self.packet.get()[length:]
                self.parse_packet(read)
            else:
                self.packet = old_packet
                break

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.ip_address = self.transport.get_extra_info("peername")[0]

    def connection_lost(self, *args):
        self.is_closed = True

        # self.save_database()

        self.transport.close()
        
    def send_old_packet(self, tokens: List[int], values: List[str]):
        self.send_packet([1, 1], ByteArray().write_utf(chr(1).join(map(str, ["".join(map(chr, tokens))] + values))).get())
        
    def send_packet(self, tokens: List[int], data: Union[ByteArray, bytes, int, List, str]):
        if self.is_closed:
            return None

        if isinstance(data, ByteArray):
            data = data.get()
        elif isinstance(data, List):
            return self.send_old_packet(tokens, data)
        elif isinstance(data, int) or isinstance(data, str):
            data = ByteArray(data).get()

        self.last_packet_id = (self.last_packet_id + 1) % 255
        
        packet = ByteArray()
        length = len(data) + 2
        packet2 = ByteArray()

        calc1 = length >> 7
        while calc1 != 0:
            packet2.write_byte(((length & 127) | 128))
            length = calc1
            calc1 = calc1 >> 7
            
        packet2.write_byte((length & 127))
        packet.write(packet2.get()).write_byte(tokens[0]).write_byte(tokens[1]).write(data)
        
        self.transport.write(packet.get())
        
    def parse_packet(self, packet: ByteArray):
        print(packet.get())