# Use a CUDA image that includes cuDNN
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04
ARG DEBIAN_FRONTEND=noninteractive

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    ffmpeg \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    && python3 -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8394
EXPOSE 8393

WORKDIR /asr-api

COPY ./src ./src
COPY ./app.py ./app.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

# Set unbuffered output for Python, facilitating real-time log output
CMD ["python3", "-u", "app.py"]
