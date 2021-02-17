import asyncio
import functools
import time

from .Client import Client
from .Server import Server
from typing import List


if __name__ == "__main__":
    repeat_text = "-=-"
    repeat_count = 24
    print(repeat_text * repeat_count)

    # Server
    start = time.time()
    main_server = Server()
    servers: List = []

    # Get the loop
    loop = asyncio.get_event_loop()

    # Listen the ports
    protocol = functools.partial(Client, main_server)
    ports: List = [11801, 12801, 13801, 14801]
    for port in ports:
        coroutine = loop.create_server(protocol, "0.0.0.0", port)
        server = loop.run_until_complete(coroutine)
        servers.append(server)

    # Startup message
    print(repeat_text * repeat_count)
    print(f"[{time.strftime('%H:%M:%S')}] Server running on ports: {ports}")
    print(f"[{time.strftime('%H:%M:%S')}] Server loaded in {time.time() - start}s.")
    print(repeat_text * repeat_count)
    print("[Server]")
    print(f"- Name: {main_server.name}")
    print(f"- Version: {main_server.version}")
    print(f"- Connection key: {main_server.connection_key}")
    print(f"- Login keys: {main_server.login_keys}")
    print(f"- Packet keys: {main_server.packet_keys}")
    print(repeat_text * repeat_count)

    # RUN
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        main_server.save_configs()
        print(f"[{time.strftime('%H:%M:%S')}] Server closed by CTRL + C.")
        print(repeat_text * repeat_count)

    # Close the server
    for server in servers:
        server.close()
        loop.run_until_complete(server.wait_closed())

    # Close the loop
    loop.close()
