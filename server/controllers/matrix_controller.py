# For if we're emulating an LED
import logging
import os
import random
from models.emulated_led import matrix as emulated_matrix

# For a live local LED
# from models.local_led import matrix as local_matrix
from models.matrix import Pixel


class MatrixController:
    def __init__(self):
        logging.info("Initializing MatrixController")
        if os.getenv("EMULATED_LED"):
            logging.info("Emulating LED")
            self.matrix = emulated_matrix()
        # else:
        #     logging.info("Using local LED")
        #     self.matrix = local_matrix()

    def randomize_matrix(self):
        _max_pixels = self.matrix.matrix.height * self.matrix.matrix.width
        # Pick a random number between 0 and the max number of pixels
        _random_pixel_count = random.randrange(_max_pixels)

        # Create a list of random pixels
        _pixels: list[Pixel] = []
        for _ in range(_random_pixel_count):
            _pixels.append({"rgb": [255, 255, 255], "position": [0, 0]})

        # Give the pixels random positions and save them in the pixels list again
        for _pixel in _pixels:
            _pixel["position"][0] = random.randrange(self.matrix.matrix.width)
            _pixel["position"][1] = random.randrange(self.matrix.matrix.height)

        print(_pixels[0])

        # Loop over the pixels and set them on the matrix
        for _pixel in _pixels:
            self.matrix.canvas.SetPixel(
                _pixel["position"][0],
                _pixel["position"][1],
                _pixel["rgb"][0],
                _pixel["rgb"][1],
                _pixel["rgb"][2],
            )

        self._update_matrix()

    def _update_matrix(self):
        self.matrix.update()
