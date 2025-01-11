import json
import random
from models.matrix import Pixel, Canvas

from rgbmatrix import RGBMatrix, RGBMatrixOptions

# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
import sys

fifo_path = "/tmp/led-matrix-fifo"
previousCanvas: Canvas = Canvas(width=64, height=32, brightness=80, pixels=[])
currentCanvas: Canvas = Canvas(width=64, height=32, brightness=80, pixels=[])


# Constants
WHITE_PIXEL = (255, 255, 255)
GREEN_PIXEL = (0, 255, 0)


def RandomPixelPositions(pixelCount: int, width: int, height: int) -> list[Pixel]:
    # TODO: Don't allow spawns in same position
    pixelPositions: list[Pixel] = []

    for x in range(pixelCount):
        randomX = random.randrange(width)
        randomY = random.randrange(height)
        pixelPositions.append(Pixel(rgb=[255, 255, 255], position=[randomX, randomY]))

    return pixelPositions


def main():
    # Setup matrix
    random.seed()
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.hardware_mapping = "regular"
    options.show_refresh_rate = True
    options.limit_refresh_rate_hz = 30
    options.gpio_slowdown = 2

    matrix = RGBMatrix(options=options)
    local_matrix_canvas = matrix.CreateFrameCanvas()
    matrix.brightness = 80

    previousCanvas = Canvas(width=64, height=32, brightness=80, pixels=[])

    # Begin Loop
    try:
        print("Press CTRL-C to stop.")
        while True:
            # Read in serialized canvas and deserialize it
            with open(fifo_path, "r") as f:
                currentCanvas = json.loads(f.read())

            # Compare the canvas to the previous canvas contents, if same then skip
            if currentCanvas == previousCanvas:
                continue

            # Reset matrix
            # matrix.Clear()

            # Loop over pixels and set them on the matrix
            for pixel in currentCanvas["pixels"]:
                local_matrix_canvas.SetPixel(
                    pixel["position"][0],
                    pixel["position"][1],
                    pixel["rgb"][0],
                    pixel["rgb"][1],
                    pixel["rgb"][2],
                )

            previousCanvas = currentCanvas

            # End loop
            matrix.SwapOnVSync(local_matrix_canvas)
            # time.sleep(0.1)

    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
