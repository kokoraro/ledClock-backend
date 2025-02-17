FROM ghcr.io/astral-sh/uv:python3.11-alpine AS runtime

ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

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
COPY --chown=docker:docker ./server ./server
COPY --chown=docker:docker pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

EXPOSE 8000

# Run the server
CMD ["uv", "run", "python", "-u", "server/server.py"]