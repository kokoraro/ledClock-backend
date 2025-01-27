# Matrix model
import datetime
import json
from typing import Union
from typing_extensions import TypedDict
from enum import Enum


class DATA_TYPE(Enum):
    MATRIX = "matrix"
    ANIMATION = "animation"


# Pixel model
class Pixel(TypedDict):
    rgb: list[int]  # RGB values
    position: list[int]  # X and Y position


# Matrix model
class Matrix(TypedDict):
    pixels: list[Pixel]
    brightness: int


# Frame model
class Frame(TypedDict):
    data: Matrix
    frame_length: int
    index: int


# Animation model
class Animation(TypedDict):
    frames: list[Frame]
    # name: str
    loop: bool


# Action request model
class ActionRequest(TypedDict):
    data_type: DATA_TYPE
    data: Union[Matrix, Animation]


class CurrentAction:
    def __init__(self, action: DATA_TYPE, data: Union[Matrix, Animation]) -> None:
        self.action: DATA_TYPE = action
        self.data: Union[Matrix, Animation] = data
        self.current_frame: int = 0
        self.time_to_change_frame: datetime.datetime = datetime.datetime.now()

    def change_action(self, action: DATA_TYPE, data: Union[Matrix, Animation]) -> None:
        self.action = action
        self.data = data
        self.current_frame = 0
        self.time_to_change_frame = datetime.datetime.now()

    def _next_frame(self) -> None:
        if self.action != DATA_TYPE.ANIMATION:
            return

        self.current_frame += 1

        # Check if we need to loop the animation
        if self.current_frame >= len(self.data["frames"]) and self.data["loop"]:
            self.current_frame = 0
            self.time_to_change_frame = datetime.datetime.now() + datetime.timedelta(
                milliseconds=self.data["frames"][self.current_frame]["frame_length"]
            )
            return

        # We don't need to loop, so keep it on the last frame
        if self.current_frame >= len(self.data["frames"]):
            self.current_frame = len(self.data["frames"]) - 1
            return

    def loop(self) -> None:
        # Only animations needs a loop atm
        if self.action != DATA_TYPE.ANIMATION:
            return

        # Check if it's time to change frame
        if datetime.datetime.now() < self.time_to_change_frame:
            return

        # Change frame
        self._next_frame()

    def get_matrix(self) -> Matrix:
        # Return matrix if it's not an animation
        if self.action != DATA_TYPE.ANIMATION:
            return self.data

        # Return current animation frame
        return self.data["frames"][self.current_frame]["data"]

    def get_action_type(self) -> DATA_TYPE:
        return self.action

    def serialize_current_action(self) -> str:
        return json.dumps(self.__dict__)


# PixelCanvas Class
class PixelCanvas:
    def __init__(
        self, width: int, height: int, brightness: int, pixels: list[Pixel]
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.brightness: int = brightness
        self.pixels: list[Pixel] = pixels

    def set_pixel(self, pixel: Pixel) -> None:
        # Find index of pixel in self.pixels
        for index, _pixel in enumerate(self.pixels):
            if _pixel["position"] == pixel["position"]:
                self.pixels[index] = pixel
                return

    def get_pixels(self) -> list[Pixel]:
        return self.pixels

    def set_pixels(self, pixels: list[Pixel]) -> None:
        self.pixels = pixels

    def serialize_canvas(self) -> str:
        return json.dumps(self.__dict__)

    def clear_canvas(self) -> None:
        for index, _pixel in enumerate(self.pixels):
            self.pixels[index]["rgb"] = [0, 0, 0]
