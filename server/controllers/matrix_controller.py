# For if we're emulating an LED
import orjson as json
import logging
import os
import random
import socket
from threading import Lock

from fastapi import HTTPException

# For a live local LED
from models.matrix import Pixel, Canvas, Animation
import time

saved_matrices_path = "saved-matrices"
saved_animations_path = "saved-animations"

MAX_LIMIT = 10

lock = Lock()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler(sys.stdout))


class MatrixController:
    def __init__(self):
        logging.info("Initializing MatrixController")
        self.canvas = Canvas(width=64, height=32, brightness=80, pixels=[])

        # Initialize the pixels
        for x in range(self.canvas.width):
            for y in range(self.canvas.height):
                self.canvas.pixels.append(Pixel(rgb=[0, 0, 0], position=[x, y]))

    # Generate random pixels and set them on the matrix
    def randomize_matrix(self):
        _max_pixels = 32
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

        # Send to driver
        driver_status = self._update_matrix()

        if driver_status != 200:
            raise HTTPException(status_code=500, detail="Error updating matrix")

        return "Successfully randomized matrix", 200

    # Set the matrix to the given matrix
    def set_matrix(self, matrix: list[Pixel]):
        start_time = time.time()

        # Set local canvas
        self.canvas.clear_canvas()
        for pixel in matrix:
            self.canvas.set_pixel(pixel)

        # Send to driver
        driver_status = self._update_matrix()
        if driver_status != 200:
            raise HTTPException(status_code=500, detail="Error updating matrix")

        # Log driver speed
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"set_matrix took {elapsed_time} seconds to run")

        return "Successfully set matrix", 200

    # Save the matrix to a file with the current date and time as the name
    def save_matrix(self, matrix: list[Pixel]):
        # Get the current date and time as a string
        current_time: str = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

        # Check if saved_matrices_path exists, if not create it
        if not os.path.exists(saved_matrices_path):
            os.makedirs(saved_matrices_path)

        # Save the matrix to a file with time as the name
        with open(f"{saved_matrices_path}/{current_time}.json", "w") as f:
            f.write(json.dumps(matrix))

        return {"filename": current_time}

    def save_animation(self, animation: Animation):
        # Get the current date and time as a string
        current_time: str = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

        # Check if animations path exists, if not create it
        if not os.path.exists(saved_animations_path):
            os.makedirs(saved_animations_path)

        # create folder for animation
        if not os.path.exists(f"{saved_animations_path}/{current_time}"):
            os.makedirs(f"{saved_animations_path}/{current_time}")
        else:
            return "Animation already exists", 400

        # Loop through frames and save them as individual files in new directory
        for index, frame in enumerate(animation["frames"]):
            with open(f"{saved_animations_path}/{current_time}/{index}.json", "w") as f:
                f.write(json.dumps(frame))

        return {"filename": current_time}

    # Delete the matrix with the given timestamp name
    def delete_matrix(self, timestamp: str):
        # Check if the file exists
        if not os.path.exists(f"{saved_matrices_path}/{timestamp}.json"):
            return "File not found", 404

        # Delete the file
        os.remove(f"{saved_matrices_path}/{timestamp}.json")

        return "File deleted"

    # Load the matrix with the given timestamp name and set it
    def load_matrix(self, timestamp: str):
        # Check if the file exists
        if not os.path.exists(f"{saved_matrices_path}/{timestamp}.json"):
            return "File not found", 404

        # Read the matrix from the file
        with open(f"{saved_matrices_path}/{timestamp}.json", "r") as f:
            matrix = json.loads(f.read())

        self.set_matrix(matrix)

        return "Matrix loaded"

    # Get the matrix with the given timestamp name and return it
    def get_matrix(self, timestamp: str):
        # Check if the file exists
        if not os.path.exists(f"{saved_matrices_path}/{timestamp}.json"):
            return "File not found", 404

        # Read the matrix from the file
        with open(f"{saved_matrices_path}/{timestamp}.json", "r") as f:
            return f.read()

    # Get a list of all the saved matrices
    def get_matrixes(self, page: int, limit: int):
        # Cap limit at MAX_LIMIT
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        # Check if directory exists
        if not os.path.exists(saved_matrices_path):
            return "Directory not found", 404

        # Get a list of all the saved matrices
        saved_matrices = os.listdir(saved_matrices_path)

        # Sort the list of matrices by date
        saved_matrices.sort()

        # Reverse the list so the most recent matrix is first
        saved_matrices.reverse()

        # Get the start and end index of the matrices we want to return
        start_index = page * limit
        end_index = start_index + limit

        # Calculate the number of pages
        number_of_pages = len(saved_matrices) // limit

        # Return the matrices
        return {
            "matrixes": saved_matrices[start_index:end_index],
            "pages": number_of_pages,
        }

    # Update the matrix locally
    def _update_matrix(self) -> bool:
        # TODO: Change this to REDIS as FIFO is blocking
        logger.info("Updating matrix")

        global lock
        # Serialize the canvas and save it to tmp directory
        with lock:
            # Open socket and conenct to server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 8888))

                # serialized_matrix = json.dumps(self.canvas.serialize_canvas()).encode(
                #     "utf-8"
                # )

                # TODO: HAVE SOME LOGIC FOR HANDLING MATRIX VS ANIMATION
                # ALSO BRIGHTNESS ETC...
                test_request = {
                    "data_type": "matrix",
                    "data": {
                        "pixels": self.canvas.get_pixels(),
                        "brightness": self.canvas.brightness,
                    },
                }

                serialized_request = json.dumps(test_request)

                # Send length of serialized matrix
                s.sendall(len(serialized_request).to_bytes(4, byteorder="big"))

                # Send matrix to server
                s.sendall(serialized_request)

                logger.info("Sent matrix to server")

                # Receive error code status from server
                response = s.recv(4)
                response = int.from_bytes(response, byteorder="big")

                return response
