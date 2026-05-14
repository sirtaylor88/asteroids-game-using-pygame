FROM python:3.13-slim

# SDL2 runtime libraries required by pygame
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependency layer (cache-friendly: copy lock files first)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Game source
COPY *.py ./
COPY core/ ./core/

# Use the virtualenv directly; disable audio (no hardware in container)
ENV PATH="/app/.venv/bin:$PATH"
ENV SDL_AUDIODRIVER=dummy

CMD ["python", "main.py"]
