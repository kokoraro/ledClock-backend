# Matrix model
from typing import TypedDict


class Pixel(TypedDict):
    rgb: list[int]  # RGB values
    position: list[int]  # X and Y position
