import glob
import importlib
import os
import time

from typing import Dict, List


TOKENS: Dict = {"recv": {}, "send": {"correct_version": [26, 3]}}


def load_token_modules():
    start = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Loading new token modules...")
    LAST_C: int = 0
    files = glob.glob("TFM/tokens/new/*/*.py")
    for index, file_name in enumerate(files):
        base_name = os.path.basename(file_name)
        if base_name == "__init__.py":
            del files[index]
            with open(file_name, "r") as file:
                data = file.read()
                lines = data.split("\n")
                for line in lines:
                    if "C" in line:
                        C = int(line.split("=")[1].replace(" ", ""))
                        if not C in TOKENS["recv"].keys():
                            TOKENS["recv"][C] = {}
                            LAST_C = C
                        else:
                            raise KeyError(f"The token C {C} is duplicated.")
    for index, file_name in enumerate(files):
        module = importlib.import_module(file_name.replace("/", ".").replace(".py", ""))
        if hasattr(module, "CC"):
            TOKENS["recv"][LAST_C][module.CC] = module
        else:
            del files[index]
            print(
                f"[{time.strftime('%H:%M:%S')}] New token module with undefined CC. C: {LAST_C}, File: {file_name}"
            )
    if len(files) > 0:
        print(
            f"[{time.strftime('%H:%M:%S')}] {len(files)} new token modules loaded in {time.time() - start}s."
        )
    else:
        print(f"[{time.strftime('%H:%M:%S')}] No new token modules were loaded.")
