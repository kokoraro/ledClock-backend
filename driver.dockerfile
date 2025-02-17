# Build the RGB Matrix driver
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS build

RUN apk update && apk add \
    sdl2-dev \
    gcc \
    freetype-dev \
    musl-dev \
    linux-headers \
    zlib-dev \
    git \
    cython \
    g++ \
    make \
    && rm -vrf /var/cache/apk/*


# Symlink cython to cython3
RUN ln -s /usr/bin/cython /usr/bin/cython3

# Install rpi-rgb-led-matrix
RUN git clone https://github.com/hzeller/rpi-rgb-led-matrix.git \
    && cd rpi-rgb-led-matrix\
    && make build-python PYTHON=$(which python3)\
    && make install-python PYTHON=$(which python3)\
    && chmod -R 777 bindings/python/rgbmatrix
    
# The final image with just the required python dependencies
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS runtime

ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install required dependencies for python packages
RUN apk update && apk add \
    sdl2-dev \
    freetype-dev \
    gcc \
    musl-dev \
    python3-dev \
    && rm -vrf /var/cache/apk/*

# Create and switch to docker user & group
RUN addgroup -S docker && adduser -S docker -G docker
USER docker

WORKDIR /app

# Copy files
COPY --chown=docker:docker ./client ./client
COPY --chown=docker:docker --from=build ./rpi-rgb-led-matrix/bindings/python/rgbmatrix ./client/rgbmatrix
COPY --chown=docker:docker ./emulator_config.json ./
COPY --chown=docker:docker pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# NOTE: Must run the container with --device /dev/mem so it can access the GPIO pins
ENTRYPOINT [ "uv", "run", "start_driver" ]