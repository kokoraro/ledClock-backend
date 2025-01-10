# For if we're emulating an LED
import logging
import os
import random
from threading import Lock

# For a live local LED
from models.matrix import Pixel, Canvas

fifo_path = "/tmp/led-matrix-fifo"
lock = Lock()


class MatrixController:
    def __init__(self):
        logging.info("Initializing MatrixController")
        self.canvas = Canvas(width=64, height=32, brightness=80, pixels=[])

        # Initialize the pixels
        for x in range(self.canvas.width):
            for y in range(self.canvas.height):
                self.canvas.pixels.append(Pixel(rgb=[0, 0, 0], position=[x, y]))

        # Create fifo pipe
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)

    def randomize_matrix(self):
        _max_pixels = self.canvas.height * self.canvas.width
        self.canvas.clear_canvas()

        # Pick a random number between 0 and the max number of pixels
        _random_pixel_count = random.randrange(_max_pixels)

        # Create a list of random pixels
        _pixels: list[Pixel] = []
        for _ in range(_random_pixel_count):
            _pixels.append({"rgb": [255, 255, 255], "position": [0, 0]})

        # Give the pixels random positions and save them in the pixels list again
        for _pixel in _pixels:
            _pixel["position"][0] = random.randrange(self.canvas.width)
            _pixel["position"][1] = random.randrange(self.canvas.height)

        # Loop over the pixels and set them on the matrix
        for _pixel in _pixels:
            self.canvas.set_pixel(_pixel)

        self._update_matrix()

    def _update_matrix(self):
        global lock
        # Serialize the canvas and save it to tmp directory
        with lock:
            with open(fifo_path, "w") as f:
                f.write(self.canvas.serialize_canvas())
