import asyncio
import configparser

from typing import Dict, List


class Server(asyncio.Transport):
    def __init__(self):
        # Instances
        self.config = configparser.ConfigParser()

        # Bool
        self.debug: bool = False

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

        # Loop
        self.loop = asyncio.get_event_loop()
        super().__init__()

    def load_configs(self):
        self.config.read("config.ini")
        TFM = self.config["Transformice"]

        self.name = str(TFM["name"])
        self.debug = bool(int(TFM["debug"]))
        self.version = int(TFM["version"])
        self.connection_key = str(TFM["connection_key"])
        self.login_keys = [int(key) for key in str(TFM["login_keys"]).split(", ")]
        self.packet_keys = [int(key) for key in str(TFM["packet_keys"]).split(", ")]

    def save_configs(self):
        with open("config.ini", "w") as file:
            self.config.write(file)

    def update_config(self, key: str, value: str):
        self.config["Transformice"][key] = value
