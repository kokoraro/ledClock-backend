import logging
import sys
import uvicorn

from fastapi import APIRouter, FastAPI
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

# Create a v1 router
v1_router = APIRouter(prefix="/v1", tags=["v1"])


# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}


# # Health endpoint
@app.get("/health")
def get_health():
    return {"status": "up"}


@app.get("/randomize-matrix", tags=["matrix"])
def get_randomize_matrix():
    matrix_controller.randomize_matrix()
    return {"status": "success"}


# Matrix endpoint
@app.post("/matrix", tags=["matrix"])
def post_matrix(matrix: list[Pixel]):
    matrix_controller.set_matrix(matrix)
    return "Sent matrix succesfully"


# Save matrix
@app.post("/save-matrix", tags=["saving"])
def post_save_matrix(matrix: list[Pixel]):
    return matrix_controller.save_matrix(matrix)


@v1_router.post("/save-animation", tags=["saving"])
def post_save_animation(animation: list[Pixel]):
    return matrix_controller.save_animation(animation)


# Load matrix
@app.post("/load-matrix", tags=["loading"])
def post_load_matrix(timestamp: str):
    return matrix_controller.load_matrix(timestamp)


# Delete matrix
@app.post("/delete-matrix", tags=["deleting"])
def delete_matrix(timestamp: str):
    return matrix_controller.delete_matrix(timestamp)


# Get matrix
@app.get("/get-matrix", tags=["getting"])
def get_matrix(timestamp: str):
    return matrix_controller.get_matrix(timestamp)


# Get matrixes
@app.get("/get-matrixes", tags=["getting"])
def get_matrixes(page: int, limit: int):
    return matrix_controller.get_matrixes(page, limit)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
