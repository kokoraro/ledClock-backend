from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, logger


class matrix:
    def __init__(self) -> None:
        logger.logging.info("Initializing Emulated LED")

        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.hardware_mapping = "regular"
        # self.options.show_refresh_rate = True
        self.options.brightness = 80
        # options.limit_refresh_rate_hz = 70

        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()

    def update(self) -> None:
        self.matrix.Clear()
        self.matrix.SwapOnVSync(self.canvas)
