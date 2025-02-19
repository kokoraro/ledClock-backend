import logging
import os
import socket
import json
import threading
from typing import Optional

from models.matrix import ActionRequest

DRIVER_HOST = os.getenv("DRIVER_HOST", "0.0.0.0")
DRIVER_PORT = os.getenv("DRIVER_PORT", 8888)

class DataReceiver(threading.Thread):
    def __init__(self, host=DRIVER_HOST, port=DRIVER_PORT):
        super().__init__()
        self.host = host
        self.port = port
        self.data = None

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Open socket and wait for connections
            s.bind((self.host, self.port))
            s.listen()

            # Log that we are listening
            logging.info(f"Listening for matrix updates on {self.host}:{self.port}")

            while True:
                #  Wait for client connection and read data
                client_socket, client_ip = s.accept()

                # Receive the length of the incoming data
                length = int.from_bytes(client_socket.recv(4), byteorder="big")

                logging.info(
                    f"Received connection from {client_ip} and expecting {length} bytes"
                )
                chunks = []
                bytes_received = 0
                while bytes_received < length:
                    chunk = client_socket.recv(min(length - bytes_received, 4096))
                    chunks.append(chunk)
                    bytes_received += len(chunk)

                logging.info(f"Done receiving {length} bytes from {client_ip}")

                # Decode data
                try:
                    input_data = json.loads(b"".join(chunks))
                except json.decoder.JSONDecodeError:
                    logging.error("Error decoding JSON")
                    logging.error(b"".join(chunks))
                    self.data = None
                    return

                # Validate data
                validation: (bool, str) = self.validate_request(input_data)
                if not validation[0]:
                    logging.error(f"Error validating request: {validation[1]}")
                    client_socket.sendall(int(400).to_bytes(4, byteorder="big"))
                    input_data = None
                else:
                    client_socket.sendall(int(200).to_bytes(4, byteorder="big"))
                    logging.info(f"Successfully validated request: {validation[1]}")

                # Close connection
                client_socket.close()

                self.data = input_data

    def get_data(self) -> Optional[ActionRequest]:
        return self.data

    def validate_request(self, data) -> (bool, str):
        if data is None:
            return (False, "Data is None")

        # Check if data looks like ActionRequest Model
        if "data_type" not in data:
            return (False, "data_type not in data")

        if "data" not in data:
            return (False, "data not in data")

        # Validate matrix request type
        match data["data_type"]:
            case "matrix":
                if not self.validate_matrix(data["data"]):
                    return (False, "data is not a valid matrix request")
            case "load_matrix":
                if not self.validate_load_matrix(data["data"]):
                    return (False, "data is not a valid load_matrix request")
            case "animation":
                if not self.validate_animation(data["data"]):
                    return (False, "data is not a valid animation request")
            case "load_animation":
                if not self.validate_load_animation(data["data"]):
                    return (False, "data is not a valid load_animation request")
            case _:
                return (False, "data_type is not valid")
        return (True, "Data is valid")

    # Validate request to load an animation from request
    def validate_matrix(self, matrix) -> bool:
        if "pixels" not in matrix:
            return False

        if "brightness" not in matrix:
            return False

        return True

    # Validate Request to load a matrix from file
    def validate_load_matrix(self, request_data) -> bool:
        if "brightness" not in request_data:
            return False

        if "timestamp" not in request_data:
            return False

        return True

    # Validate request to load an animation from request
    def validate_animation(self, animation) -> bool:
        if "frames" not in animation:
            return False

        if "loop" not in animation:
            return False

        return True

    # Validate request to load an animation from file
    def validate_load_animation(self, request_data) -> bool:
        if "timestamp" not in request_data:
            return False

        return True
