# Matrix model
from typing_extensions import TypedDict


class Pixel(TypedDict):
    rgb: list[int]  # RGB values
    position: list[int]  # X and Y position


class Canvas(TypedDict):
    width: int
    height: int
    brightness: int
    pixels: list[Pixel]
