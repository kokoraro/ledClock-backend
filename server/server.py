import uvicorn
from fastapi import FastAPI
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from models.matrix import Pixel

app = FastAPI()


# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}


# Health endpoint
@app.get("/health")
def get_health():
    return {"status": "up"}


# Matrix endpoint
@app.post("/matrix")
def post_matrix(matrix: list[Pixel]):
    # Process the matrix here
    return {"received matrix": matrix[0]}


# Setup LED matrix
def setupMatrix():
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.hardware_mapping = "regular"
    # options.show_refresh_rate = True
    options.limit_refresh_rate_hz = 70

    matrix = RGBMatrix(options=options)

    return matrix


if __name__ == "__main__":
    uvicorn.run(
        "server:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["server"]
    )
