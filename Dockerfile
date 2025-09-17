# syntax=docker/dockerfile:1

# The Dockerfile reference guide at https://docs.docker.com/go/dockerfile-reference/

# ARG POETRY_VERSION=2.1.4

FROM python:3.9-slim

ENV NODE_ENV=production

# System dependencies
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    nodejs \
    npm \
    lsof \
    && curl -sSL 'https://install.python-poetry.org' | python - \
    # Cleaning cache:
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Path to poetry must be added to PATH
ENV PATH="$PATH:/root/.local/bin"

WORKDIR /app

RUN mkdir -p logs server/test_reports e2e/logs e2e/test_reports

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a bind mount to avoid having to copy them into the layer.
# Leverage a cache mount to speed up subsequent builds.
RUN --mount=type=bind,source=client/package.json,target=client/package.json \
    --mount=type=bind,source=client/package-lock.json,target=client/package-lock.json \
    --mount=type=cache,target=/root/.npm \
    cd client && npm ci --omit=dev

COPY server/readme.md server/server.py ./server/

RUN --mount=type=cache,target=root/.local/share/pypoetry \
    --mount=type=bind,source=server/pyproject.toml,target=server/pyproject.toml \
    --mount=type=bind,source=server/poetry.lock,target=server/poetry.lock \
    cd server && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the source files into the image.
COPY . .

SHELL ["/bin/bash", "-c"]

# Run the application as a non-root user.
# USER node

EXPOSE 3000 8000 8001

# Run the application.
CMD npm run start:prod true
