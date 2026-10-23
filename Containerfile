FROM debian:trixie-backports

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN python3 -m venv .venv/ && \
    source .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

CMD source .venv/bin/activate && /bin/sh
