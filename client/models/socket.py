import socket
import json
import threading
from typing import Optional

from models.matrix import ActionRequest


class DataReceiver(threading.Thread):
    def __init__(self, host="localhost", port=7777):
        super().__init__()
        self.host = host
        self.port = port
        self.data = None

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            chunks = []
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                chunks.append(chunk)
            try:
                input_data = json.loads(b"".join(chunks).decode("utf-8"))
            except json.decoder.JSONDecodeError:
                print("Error decoding JSON")
                print(b"".join(chunks).decode("utf-8"))
                self.data = None
                return

            if not self.validate_request(input_data):
                print("Error validating request")
                self.data = None
                return

            self.data = input_data

    def get_data(self) -> Optional[ActionRequest]:
        return self.data

    def validate_request(self, data) -> bool:
        if data is None:
            return False

        # Check if data looks like ActionRequest Model
        if "data_type" not in self.data:
            return False

        # Validate matrix request type
        if self.data["data_type"] == "matrix":
            if not self.validate_matrix(self.data["data"]):
                return False

        # Validate animation request type
        if self.data["data_type"] == "animation":
            if not self.validate_animation(self.data["data"]):
                return False

        return True

    def validate_matrix(self, matrix) -> bool:
        if "pixels" not in matrix:
            return False

        if "brightness" not in matrix:
            return False

        return True

    def validate_animation(self, animation) -> bool:
        if "frames" not in animation:
            return False

        if "loop" not in animation:
            return False

        return True
