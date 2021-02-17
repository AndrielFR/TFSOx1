import asyncio

from .utils.ByteArray import ByteArray


class Client(asyncio.Protocol):
    def __init__(self, server):
        # Instances
        self.server: Server = server
        self.transport: asyncio.Transport = None

        # Bool
        self.is_closed: bool = False

        # Integer
        self.id: int = 0

        # String
        self.name: str = ""
        self.ip_address: str = "0.0.0.0"

        # Loop
        self.loop = asyncio.get_event_loop()
        super().__init__(server=self.server)

    def data_received(self, packet: bytes):
        if len(packet) < 2:
            return None

        if packet.startswith(b"<policy-file-request/>"):
            self.transport.write(
                b'<cross-domain-policy><allow-access-from domain="*" to-ports="*"/></cross-domain-policy>'
            )
            return self.transport.close()

        packet = ByteArray(packet)
        print(str(packet), len(packet))

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.ip_address = self.transport.get_extra_info("peername")[0]

    def connection_lost(self, *args):
        self.is_closed = True

        # self.save_database()

        self.transport.close()