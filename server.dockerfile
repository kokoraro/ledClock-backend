FROM python:3.11-alpine AS runtime

ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

# Create docker user & group
RUN addgroup -S docker && adduser -S docker -G docker

# Switch to docker user
USER docker

WORKDIR /app

# Copy files
COPY --chown=docker:docker ./client ./client
COPY --chown=docker:docker ./server ./server

# Install dependencies
WORKDIR /app/server
RUN pipenv install --deploy --ignore-pipfile

EXPOSE 8000

# Run the server
CMD ["pipenv", "run", "python", "-u", "server.py"]