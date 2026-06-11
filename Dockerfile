FROM python:3.11-slim

LABEL maintainer="Variant 46"
LABEL description="Parametric Scatter Blender Add-on - CI/Testing environment"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxfixes3 \
    libxi6 \
    libxxf86vm1 \
    libxkbcommon0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-dri \
    libegl1 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

ENV BLENDER_PATH=/opt/blender

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "/app/entrypoint.sh"]
