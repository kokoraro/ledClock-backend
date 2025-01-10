from rgbmatrix import RGBMatrix, RGBMatrixOptions


class matrix:
    def __init__(self) -> None:
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.hardware_mapping = "regular"
        self.options.show_refresh_rate = True
        # options.limit_refresh_rate_hz = 70

        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()

        self.canvas.SetPixel(20, 0, 255, 255, 255)
        self.canvas.SetPixel(23, 0, 255, 255, 255)
        self.update()

    def update(self) -> None:
        self.matrix.Clear()
        self.matrix.SwapOnVSync(self.canvas)
