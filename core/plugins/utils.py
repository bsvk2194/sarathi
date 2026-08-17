"""
Plugin utility functions.
"""

import json
from pathlib import Path


CONFIG_DIRECTORY = Path("configs")


def ensure_directory():

    CONFIG_DIRECTORY.mkdir(
        exist_ok=True
    )


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(
    path,
    data
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )