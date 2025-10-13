# syntax=docker/dockerfile:1
FROM python:3.9-slim

ENV NODE_ENV=production

# System dependencies
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    nodejs \
    npm \
    lsof \
    && curl -sSL 'https://install.python-poetry.org' | POETRY_HOME=/opt/poetry python - \
    # Clean caches:
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Use system-wide poetry installation
ENV PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Create 'doctor' user and group EARLY
RUN groupadd -r doctor && useradd -r -g doctor -m -d /home/doctor doctor

# Create directories with proper ownership from the start
RUN mkdir -p logs server/test_reports e2e/logs e2e/test_reports \
    && chown -R doctor:doctor /app

# Install client dependencies AS ROOT (for now) but fix cache location
RUN --mount=type=bind,source=client/package.json,target=client/package.json \
    --mount=type=bind,source=client/package-lock.json,target=client/package-lock.json \
    --mount=type=cache,target=/tmp/.npm \
    cd client && npm ci --omit=dev --cache /tmp/.npm

# Copy server files with proper ownership
COPY --chown=doctor:doctor server/readme.md server/server.py ./server/

# Install Python dependencies AS ROOT but use accessible cache location
RUN --mount=type=cache,target=/tmp/poetry-cache \
    --mount=type=bind,source=server/pyproject.toml,target=server/pyproject.toml \
    --mount=type=bind,source=server/poetry.lock,target=server/poetry.lock \
    cd server && \
    poetry config cache-dir /tmp/poetry-cache && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.path /app/server/.venv && \
    poetry install --no-interaction --no-ansi

# Copy source files with proper ownership
COPY --chown=doctor:doctor . .

# Fix any permission issues that might have occurred
RUN chown -R doctor:doctor /app

# Test Python packages are installed correctly in venv
RUN /app/server/.venv/bin/python -c "import fastapi; print('FastAPI installed successfully')"


# Use bash as default shell
SHELL ["/bin/bash", "-c"]

# Switch to non-root user
USER doctor

EXPOSE 3000 8000 8001

CMD npm run start:prod true
