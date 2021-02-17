import asyncio
import functools
import time

from .Client import Client
from .Server import Server
from typing import List


if __name__ == "__main__":
    # Server
    start = time.time()
    server = Server()

    # Get the loop
    loop = asyncio.get_event_loop()

    # Listen the ports
    protocol = functools.partial(Client, server)
    ports: List = [11801, 12801, 13801, 14801]
    for port in ports:
        coroutine = loop.create_server(protocol, "0.0.0.0", port)
        loop.run_until_complete(coroutine)

    # Startup message
    repeat_text = "-=-"
    repeat_count = 22
    print(repeat_text * repeat_count)
    print(f"[{time.strftime('%H:%M:%S')}] Server running on ports: {ports}")
    print(
        f"[{time.strftime('%H:%M:%S')}] Server loaded in {time.time() - start / 1000}ms."
    )
    print(repeat_text * repeat_count)
    print("[Server]")
    print(f"- Name: {server.name}")
    print(f"- Version: {server.version}")
    print(f"- Connection key: {server.connection_key}")
    print(f"- Login keys: {server.login_keys}")
    print(f"- Packet keys: {server.packet_keys}")
    print(repeat_text * repeat_count)

    # RUN
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.save_configs()
        print(f"[{time.strftime('%H:%M:%S')}] Server closed by CTRL + C.")
        print(repeat_text * repeat_count)
