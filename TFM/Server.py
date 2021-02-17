import asyncio
import configparser
import time

from .Tokens import load_token_modules
from typing import Dict, List


class Server(asyncio.Transport):
    def __init__(self):
        # Instances
        self.config = configparser.ConfigParser()

        # Bool
        self.is_debug: bool = False

        # Dict
        self.players: Dict = {}

        # Integer
        self.version: int = 0

        # List
        self.login_keys: List = []
        self.packet_keys: List = []

        # String
        self.name: str = ""
        self.connection_key: str = ""

        # Load configurations
        self.load_configs()

        # Load modules
        load_token_modules()

        # Loop
        self.loop = asyncio.get_event_loop()

    def load_configs(self):
        start = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Loading configurations...")
        self.config.read("config.ini")
        TFM = self.config["Transformice"]

        self.name = str(TFM["name"])
        self.is_debug = bool(int(TFM["debug"]))
        self.version = int(TFM["version"])
        self.connection_key = str(TFM["connection_key"])
        self.login_keys = [int(key) for key in str(TFM["login_keys"]).split(", ")]
        self.packet_keys = [int(key) for key in str(TFM["packet_keys"]).split(", ")]
        print(
            f"[{time.strftime('%H:%M:%S')}] Configurations loaded in {time.time() - start}s."
        )

    def save_configs(self):
        with open("config.ini", "w") as file:
            self.config.write(file)

    def update_config(self, key: str, value: str):
        self.config["Transformice"][key] = value
