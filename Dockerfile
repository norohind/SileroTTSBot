FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install git gcc -y --no-install-recommends && apt clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install Cython && \
    pip wheel --no-deps --wheel-dir /app/wheels -r requirements.txt && \
    pip wheel torch numpy --wheel-dir /app/wheels --index-url https://download.pytorch.org/whl/cpu



FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -ms /bin/bash silero_user &&  \
    apt update && apt install ffmpeg -y --no-install-recommends && apt clean && rm -rf /var/lib/apt/lists/* \
USER silero_user

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

CMD ["python3", "/app/main.py"]
