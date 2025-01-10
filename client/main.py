import random
from typing import List

# from rgbmatrix import RGBMatrix, RGBMatrixOptions

from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
import time
import sys

# import curses

# Constants
WHITE_PIXEL = (255, 255, 255)
GREEN_PIXEL = (0, 255, 0)


class RGB:
    def __init__(self, r=255, g=255, b=255):
        self.r = r
        self.g = g
        self.b = b


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Pixel:
    def __init__(self, rgb: RGB = RGB(), position: Position = Position()):
        self.rgb = rgb
        self.position = position


def RandomPixelPositions(pixelCount: int, width: int, height: int) -> List[Pixel]:
    # TODO: Don't allow spawns in same position
    pixelPositions: List[Pixel] = []

    for x in range(pixelCount):
        randomX = random.randrange(width)
        randomY = random.randrange(height)
        pixelPositions.append(Pixel(RGB(), Position(randomX, randomY)))

    return pixelPositions


# def cursesTerminal():
#     screen = curses.initscr()
#     screen.addstr("Hello, World!")
#     screen.refresh()
#     screen.getch()
#     curses.endwin()


def main():
    # cursesTerminal()

    random.seed()
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.hardware_mapping = "regular"
    options.show_refresh_rate = True
    options.limit_refresh_rate_hz = 70

    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()
    matrix.brightness = 80
    # matrix.Fill(255, 0, 0)

    try:
        print("Press CTRL-C to stop.")
        while True:
            pixels = RandomPixelPositions(30, matrix.width, matrix.height)
            matrix.Clear()
            pixel: Pixel

            for pixel in pixels:
                canvas.SetPixel(
                    pixel.position.x,
                    pixel.position.y,
                    pixel.rgb.r,
                    pixel.rgb.g,
                    pixel.rgb.b,
                )

            matrix.SwapOnVSync(canvas)
            time.sleep(0.1)

    except KeyboardInterrupt:
        # curses.endwin()
        sys.exit(0)


if __name__ == "__main__":
    main()
