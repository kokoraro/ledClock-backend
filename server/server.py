import logging
import sys
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.matrix import Pixel
from controllers.matrix_controller import MatrixController

app = FastAPI()
matrix_controller = MatrixController()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.info("API is starting up")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    matrix_controller.set_matrix(matrix)
    return "Sent matrix succesfully"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
