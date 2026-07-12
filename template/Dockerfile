# syntax=docker/dockerfile:1
#
# Multi-stage build: dependencies are resolved and installed in `builder` from the
# committed uv.lock, then only the resulting virtualenv and source are copied into a
# slim runtime image. Keeps the runtime image free of uv, build tools, and the wheel
# cache. See docs.astral.sh/uv/guides/integration/docker/ (SOURCES.md).

FROM python:{{PYTHON_VERSION}}-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies before copying source so dependency layers stay cached across
# source-only changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:{{PYTHON_VERSION}}-slim

RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

# Placeholder process command: this harness is framework-agnostic and ships no
# `__main__` or ASGI app by design (see docs/ARCHITECTURE.md). Replace with the
# project's real entrypoint, e.g.:
#   CMD ["uvicorn", "{{PACKAGE_NAME}}.entrypoints.http:app", "--host", "0.0.0.0", "--port", "8000"]
#   CMD ["python", "-m", "{{PACKAGE_NAME}}"]
CMD ["python", "-c", "import {{PACKAGE_NAME}}; print({{PACKAGE_NAME}}.__doc__)"]
