import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.matrix import Pixel
from controllers.matrix_controller import MatrixController

app = FastAPI()
matrix_controller = MatrixController()

origins = [
    "http://localhost:3001",
    "http://192.168.86.*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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
    return {"received matrix": matrix}


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
