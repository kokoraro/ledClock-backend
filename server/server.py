import uvicorn
import logging

from fastapi import FastAPI
from http.server import HTTPServer, BaseHTTPRequestHandler

from models.matrix import Pixel
from controllers.matrix_controller import MatrixController

app = FastAPI()
matrix_controller = MatrixController()


# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}


# # Health endpoint
@app.get("/health")
def get_health():
    return {"status": "up"}


@app.get("/randomize-matrix")
def get_randomize_matrix():
    matrix_controller.randomize_matrix()
    return {"status": "success"}


# Matrix endpoint
@app.post("/matrix")
def post_matrix(matrix: list[Pixel]):
    # Process the matrix here
    return {"received matrix": matrix[0]}


# class MyServer(BaseHTTPRequestHandler):
#     def do_GET(self):
#         # Handle randomize endpoint
#         if self.path == "/randomize-matrix":
#             matrix_controller.randomize_matrix()
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(b"Randomized matrix")
#             return

#         if self.path == "/health":
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(b'{"status": "up"}')
#             return

#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"Hello, world!")

#     def do_POST(self):
#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"Hello, world!")


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    # # matrix_controller = MatrixController()

    # # start the web server
    # server_address = ("localhost", 8000)
    # httpd = HTTPServer(server_address, MyServer)
    # logging.info("Starting httpd...\n")

    # try:
    #     httpd.serve_forever()
    # except KeyboardInterrupt:
    #     pass

    # httpd.server_close()
    # logging.info("Stopping httpd...\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
