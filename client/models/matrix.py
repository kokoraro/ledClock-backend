# Matrix model
from __future__ import annotations
import datetime
import logging
import os
import orjson as json
from typing import Union
from typing_extensions import TypedDict
from enum import Enum


class DATA_TYPE(Enum):
    MATRIX = "matrix"
    LOAD_MATRIX = "load_matrix"
    ANIMATION = "animation"
    LOAD_ANIMATION = "load_animation"


# Pixel model
class Pixel(TypedDict):
    rgb: list[int]  # RGB values
    position: list[int]  # X and Y position


# Matrix model
class Matrix(TypedDict):
    pixels: list[Pixel]
    brightness: int


# Load matrix model from file
class LoadMatrix(TypedDict):
    brightness: int
    timestamp: str


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


# Load animation model from file
class LoadAnimation(TypedDict):
    timestamp: str


# Action request model
class ActionRequest(TypedDict):
    data_type: DATA_TYPE
    data: Union[Matrix, Animation, LoadMatrix, LoadAnimation]


class CurrentAction:
    def __init__(self, action: DATA_TYPE, data: Union[Matrix, Animation]) -> None:
        self.action: DATA_TYPE = action
        self.data: Union[Matrix, Animation] = data
        self.current_frame: int = 0
        self.time_to_change_frame: datetime.datetime = datetime.datetime.now()
        self.last_handled_action_request: bytes = b""

    def change_action(
        self,
        action: DATA_TYPE,
        data: Union[Matrix, Animation, LoadMatrix, LoadAnimation],
    ) -> None:
        logging.info(f"Changing action to {action}")

        if action in [DATA_TYPE.LOAD_MATRIX.value, DATA_TYPE.LOAD_ANIMATION.value]:
            # Got a request to load from saved files, let's convert it
            if self.convert_action(action, data):
                logging.info("Successfully converted action")
                return

            # Failed to convert action, so let's keep the status quo
            logging.warn("Failed to convert action")
            return

        self.data = data
        self.current_frame = 0

        # Got a request to set the matrix or animation
        # Convert action to DATA_TYPE
        match action:
            case DATA_TYPE.MATRIX.value:
                self.action = DATA_TYPE.MATRIX
                self.time_to_change_frame = datetime.datetime.now()
            case DATA_TYPE.ANIMATION.value:
                self.action = DATA_TYPE.ANIMATION
                self.time_to_change_frame = (
                    datetime.datetime.now()
                    + datetime.timedelta(
                        milliseconds=self.data["frames"][self.current_frame][
                            "frame_length"
                        ]
                    )
                )

    def convert_action(
        self, action: DATA_TYPE, data: Union[LoadMatrix, LoadAnimation]
    ) -> bool:
        if action == DATA_TYPE.LOAD_MATRIX.value:
            # Attempt to load matrix from file
            try:
                with open(f"saved-matrices/{data['timestamp']}.json", "r") as f:
                    matrix = json.loads(f.read())
            except FileNotFoundError:
                logging.warn(f"Failed to find matrix '{data['timestamp']}.json'")
                return False

            # NOTE: Old format has just pixel data in a list, new format has brightness too in the form of an object
            # Let's workout what format is saved and convert it to the new format

            # check if matrix is a list or dict
            if isinstance(matrix, list):
                # Old format, convert to new format
                matrix = {"pixels": matrix, "brightness": 80}

            # Check if data request overrides brightness
            if "brightness" in data:
                matrix["brightness"] = data["brightness"]

            self.action = DATA_TYPE.MATRIX
            self.data = matrix
            return True

        if action == DATA_TYPE.LOAD_ANIMATION.value:
            # Attempt to load animation from file

            # Validate that the animation folder exists
            if not os.path.exists(f"saved_animations/{data['timestamp']}"):
                return False

            # Find how many frames there are for the animation in the directory
            frame_count = 0
            while os.path.exists(
                f"saved_animations/{data['timestamp']}/{frame_count}.json"
            ):
                frame_count += 1

            # Escape if there aren't any frames
            if frame_count == 0:
                return False

            # Loop over frames and build animation
            frames = []
            for frame_index in range(frame_count):
                with open(
                    f"saved_animations/{data['timestamp']}/{frame_index}.json", "r"
                ) as f:
                    frame = json.loads(f.read())
                    frames.append(frame)

            built_animation = Animation(frames=frames, loop=False)

            # Load meta file
            try:
                with open(f"saved_animations/{data['timestamp']}/meta.json", "r") as f:
                    meta = json.loads(f.read())
                    built_animation["loop"] = meta["loop"]
            except FileNotFoundError:
                logging.warn(
                    f"Failed to load meta file for animation {data['timestamp']}"
                )

            # Check if request overrides loop
            if "loop" in data:
                built_animation["loop"] = data["loop"]

            self.action = DATA_TYPE.ANIMATION
            self.data = built_animation
            return True

        # Unknown action
        logging.warn(f"Unknown action {action}")
        return False

    def _next_frame(self) -> None:
        if self.action != DATA_TYPE.ANIMATION:
            return

        self.current_frame += 1

        # Check if we need to loop the animation
        if self.current_frame >= len(self.data["frames"]):
            if not self.data["loop"]:
                # We're not looping so keep on the last frame
                self.current_frame = len(self.data["frames"]) - 1
                self.time_to_change_frame = (
                    datetime.datetime.now() + datetime.timedelta(seconds=3600)
                )
                return

            # loop back to start
            self.current_frame = 0

        # Set time to change frame
        self.time_to_change_frame = datetime.datetime.now() + datetime.timedelta(
            milliseconds=self.data["frames"][self.current_frame]["frame_length"]
        )

    def loop(self) -> None:
        # Only animations needs a loop atm
        if self.action != DATA_TYPE.ANIMATION:
            return

        # Check if it's time to change frame
        if datetime.datetime.now() < self.time_to_change_frame:
            return

        logging.info(f"Changing frame! Current frame: {self.current_frame}")
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

    def get_last_handled_action_request(self) -> bytes:
        return self.last_handled_action_request

    def set_last_handled_action_request(self, request: bytes) -> None:
        self.last_handled_action_request = request

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

    def set_brightness(self, brightness: int) -> None:
        self.brightness = brightness

    def copy(self, other: PixelCanvas) -> None:
        self.width = other.width
        self.height = other.height
        self.brightness = other.brightness
        self.pixels = other.pixels.copy()

    def set_pixels(self, pixels: list[Pixel]) -> None:
        self.pixels = pixels

    def serialize_canvas(self) -> str:
        return json.dumps(self.__dict__)

    def get_hash(self) -> str:
        return hash(self.serialize_canvas())

    def clear_canvas(self) -> None:
        for index, _pixel in enumerate(self.pixels):
            self.pixels[index]["rgb"] = [0, 0, 0]
