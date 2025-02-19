import orjson as json
import logging
import os
import sys
import random
import time
from typing import Optional

from models.socket import DataReceiver
from models.matrix import (
    ActionRequest,
    CurrentAction,
    Matrix,
    Pixel,
    PixelCanvas,
    DATA_TYPE,
)

# Use emulator if running locally
if os.getenv("LOCAL_DEV"):
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    from RGBMatrixEmulator.emulators.canvas import Canvas
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, FrameCanvas as Canvas

# Constants
WHITE_PIXEL = (255, 255, 255)
GREEN_PIXEL = (0, 255, 0)


def RandomPixelPositions(pixelCount: int, width: int, height: int) -> list[Pixel]:
    # TODO: Don't allow spawns in same position
    pixelPositions: list[Pixel] = []

    for x in range(pixelCount):
        randomX = random.randrange(width)
        randomY = random.randrange(height)
        pixelPositions.append(
            Pixel(rgb=[255, 255, 255], position=[randomX, randomY]))

    return pixelPositions


def matrix_init() -> (RGBMatrix, Canvas):
    # Setup matrix options
    random.seed()
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.hardware_mapping = "regular"
    options.show_refresh_rate = False
    options.limit_refresh_rate_hz = 70
    options.gpio_slowdown = 2
    # options.pwm_dither_bits = 1
    # options.pwm_lsb_nanoseconds = 50

    # Create matrix
    matrix_driver = RGBMatrix(options=options)
    matrix_driver.brightness = 80

    # Create Canvas
    matrix_driver_canvas = matrix_driver.CreateFrameCanvas()

    # Set initial matrix
    matrix_driver.SwapOnVSync(matrix_driver_canvas)

    return (matrix_driver, matrix_driver_canvas)


def matrix_loop(
    matrix_driver: RGBMatrix,
    matrix_driver_canvas: Canvas,
    previousCanvas: PixelCanvas,
    currentCanvas: PixelCanvas,
) -> PixelCanvas:
    time.sleep(0.1)

    # Compare the canvas to the previous canvas contents, if same then skip
    if currentCanvas.get_hash() == previousCanvas.get_hash():
        return previousCanvas

    logging.info("Displaying new matrix")

    matrix_driver.Clear()

    # Loop over pixels and set them on the matrix
    for pixel in currentCanvas.get_pixels():
        matrix_driver_canvas.SetPixel(
            pixel["position"][0],
            pixel["position"][1],
            pixel["rgb"][0],
            pixel["rgb"][1],
            pixel["rgb"][2],
        )

    previousCanvas.copy(currentCanvas)

    # End loop
    matrix_driver.SwapOnVSync(matrix_driver_canvas)

    return previousCanvas


def determine_current_canvas(
    current_action: CurrentAction, canvas: PixelCanvas
) -> PixelCanvas:
    current_matrix_pixels = current_action.get_matrix()["pixels"]
    canvas.set_pixels(current_matrix_pixels)
    return canvas


def update_action(
    request: ActionRequest, current_action: CurrentAction
) -> CurrentAction:
    if request is None:
        return current_action

    # Check if data looks like ActionRequest Model
    if "data_type" not in request:
        return current_action

    # Check if the action is already being handled
    if current_action.get_last_handled_action_request() == json.dumps(request):
        return current_action

    current_action.change_action(
        action=request["data_type"], data=request["data"])
    current_action.set_last_handled_action_request(json.dumps(request))

    return current_action


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Setup matrix driver and canvas
    matrix_driver, matrix_driver_canvas = matrix_init()

    # Prepare canvas structures
    current_canvas: Optional[PixelCanvas] = PixelCanvas(
        width=64, height=32, brightness=80, pixels=[]
    )
    previous_canvas = PixelCanvas(
        width=64, height=32, brightness=80, pixels=[])

    # Setup current action
    current_matrix: Matrix = {
        "pixels": current_canvas.get_pixels(), "brightness": 80}
    current_action: CurrentAction = CurrentAction(
        action=DATA_TYPE.MATRIX, data=current_matrix
    )

    # Start a seperate thread to read from socket
    data_receiver = DataReceiver()
    data_receiver.start()

    # Begin Loop
    logging.info("Press CTRL-C to stop.")
    try:
        while True:
            # Determine the current action and update it
            current_action = update_action(
                request=data_receiver.get_data(), current_action=current_action
            )
            current_action.loop()

            # Determine the current canvas to display from the current action
            current_canvas = determine_current_canvas(
                current_action=current_action, canvas=current_canvas
            )

            if current_canvas is None:
                logging.info("current_canvas is None")
                current_canvas = previous_canvas

            previous_canvas = matrix_loop(
                matrix_driver=matrix_driver,
                matrix_driver_canvas=matrix_driver_canvas,
                previousCanvas=previous_canvas,
                currentCanvas=current_canvas,
            )

    except KeyboardInterrupt:
        data_receiver.join()
        sys.exit(0)


if __name__ == "__main__":
    main()
