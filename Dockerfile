FROM python:3.11-slim

LABEL maintainer="Variant 46"
LABEL description="Parametric Scatter Blender Add-on - CI/Testing environment"

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    libxfixes3 \
    libxi6 \
    libxxf86vm1 \
    libxkbcommon0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

ENV BLENDER_VERSION=4.2.0
ENV BLENDER_URL="https://download.blender.org/release/Blender4.2/blender-${BLENDER_VERSION}-linux-x64.tar.xz"

RUN wget -q "${BLENDER_URL}" -O /tmp/blender.tar.xz \
    && tar -xf /tmp/blender.tar.xz -C /opt/ \
    && rm /tmp/blender.tar.xz \
    && ln -s /opt/blender-${BLENDER_VERSION}-linux-x64/blender /usr/local/bin/blender

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN blender --background --python-expr "print('Blender ready')"

CMD ["blender", "--background", "--python", "tests/run_tests.py"]
