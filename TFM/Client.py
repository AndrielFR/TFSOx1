import asyncio
import random

from .Tokens import TOKENS
from .utils.ByteArray import ByteArray
from typing import List, Union


class Client(asyncio.Protocol):
    def __init__(self, server):
        # Instances
        self.byte: ByteArray = ByteArray()
        self.server: Server = server
        self.transport: asyncio.Transport = None

        # Bool
        self.is_closed: bool = False
        self.validating_version: bool = False

        # Integer
        self.id: int = 0
        self.last_packet_id: int = random.randint(0, 99)
        self.auth_key: int = random.randint(0, 2147483647)

        # String
        self.tag: str = ""
        self.name: str = ""
        self.username: str = ""
        self.ip_address: str = "0.0.0.0"

        # Loop
        self.loop = asyncio.get_running_loop()

    def get_new_len(self, b: ByteArray):
        var_2068 = 0
        var_2053 = 0
        var_176 = b
        while var_2053 < 10:
            var_56 = var_176.read_byte() & 255
            var_2068 |= (var_56 & 127) << 7 * var_2053
            var_2053 += 1
            if var_56 & 128 != 128 or var_2053 >= 5:
                return var_2068 + 1, var_2053

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

        self.byte.write(packet)
        old_packet = self.byte.copy()
        while len(self.byte) > 0:
            length, lenlen = self.get_new_len(self.byte)
            if len(self.byte) >= length:
                read = ByteArray(self.byte.get()[:length])
                old_packet.packet = old_packet.get()[length:]
                self.byte.packet = self.byte.get()[length:]
                self.loop.create_task(self.parse_packet(read))
            else:
                self.byte = old_packet
                break

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.ip_address = self.transport.get_extra_info("peername")[0]

        if self.username not in self.server.players.keys():
            self.server.players[self.username] = self

    def connection_lost(self, *args):
        self.is_closed = True

        # self.save_database()

        if self.username in self.server.players.keys():
            del self.server.players[self.username]

        self.transport.close()

    async def send_old_packet(self, tokens: List[int], values: List[str]):
        await self.send_packet(
            [1, 1],
            ByteArray()
            .write_utf(chr(1).join(map(str, ["".join(map(chr, tokens))] + values)))
            .get(),
        )

    async def send_packet(
        self, tokens: List[int], data: Union[ByteArray, bytes, int, List, str]
    ):
        if self.is_closed:
            return None

        if isinstance(data, ByteArray):
            data = data.get()
        elif isinstance(data, List):
            return await self.send_old_packet(tokens, data)
        elif isinstance(data, (int, str)):
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
        packet.write(packet2.get()).write_byte(tokens[0]).write_byte(tokens[1]).write(
            data
        )

        self.transport.write(packet.get())

    async def parse_packet(self, packet: ByteArray):
        if self.is_closed:
            return None

        packet_id, C, CC = packet.read_byte(), packet.read_byte(), packet.read_byte()

        parsing: bool = False

        if not self.validating_version:
            if C == 28 and CC == 1:
                parsing = True
                version, connection_key = packet.read_short(), packet.read_utf()

                text = "[New user]\n"
                text += f"- IP: {self.ip_address}\n"

                invalid: bool = False

                if version != self.server.version:
                    invalid = True
                    text += f"- Invalid version: {version}, correct: {self.server.version}\n"
                if connection_key != self.server.connection_key:
                    invalid = True
                    text += f"- Invalid connection key: {connection_key}, correct: {self.server.connection_key}\n"
                if invalid or self.server.is_debug:
                    print(text)
                if invalid:
                    self.transport.close()
                else:
                    self.validating_version = True
                    await self.send_correct_version()
            else:
                self.transport.close()
        else:
            if C in TOKENS["recv"].keys() and CC in TOKENS["recv"][C].keys():
                module = TOKENS["recv"][C][CC]
                parsing = True
                try:
                    await module.parse(self, self.server, packet)
                except Exception as excep:
                    print(excep)

        if not parsing and self.server.is_debug:
            print(f"New token found: [{C}, {CC}], Packet: {packet.get()}")

    async def send_correct_version(self, community: str = "EN"):
        await self.send_packet(
            TOKENS["send"]["correct_version"],
            ByteArray()
            .write_int(len(self.server.players))
            .write_utf(community)
            .write_utf(community)
            .write_int(self.auth_key)
            .write_bool(False),
        )
