# syntax=docker/dockerfile:1

# The Dockerfile reference guide at https://docs.docker.com/go/dockerfile-reference/

# ARG NODE_VERSION=23.6.0

FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    nodejs \
    npm \
    # build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

# ENV NODE_ENV production

WORKDIR /app

# Copy the source files into the image.
COPY . .

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a bind mounts to package.json and package-lock.json to avoid having to copy them into this layer.
# Leverage a cache mount to /root/.npm to speed up subsequent builds.
RUN --mount=type=bind,source=client/package.json,target=client/package.json \
    --mount=type=bind,source=client/package-lock.json,target=client/package-lock.json \
    --mount=type=cache,target=/root/.npm \
    cd client && npm ci --omit=dev

RUN --mount=type=bind,source=server/pyproject.toml,target=server/pyproject.toml \
    --mount=type=bind,source=server/poetry.lock,target=server/poetry.lock \
    --mount=type=cache,target=/root/.cache/pypoetry \
    cd server && poetry install

SHELL ["/bin/bash", "-c"]
RUN mkdir -p logs
RUN bash utils/setup-app.sh > logs/docker-setup.log 2>&1

# Run the application as a non-root user.
# USER node

# Expose the ports that the application listens on.
EXPOSE 8000 3000

# Run the application.
CMD bash utils/start.sh true
