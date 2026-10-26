#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <directory_to_mount> [agent_options...]"
    echo ""
    echo "Example: $0 ./my_project_folder -u http://host.containers.internal:5001/v1/ -m google/gemma-4-31B"
    exit 1
fi

TARGET_DIR=$(realpath "$1")
shift

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

echo "Starting sandbox..."
echo "Mounting: $TARGET_DIR -> /sandbox"
echo "Agent options: $*"
echo "Press Ctrl+C to stop the container."

podman run --rm -it \
    -v "$TARGET_DIR:/sandbox:Z" \
    --name agent_sandbox \
    agent_image \
    /bin/bash -c "source .venv/bin/activate && cd /sandbox && python3 /app/main.py $*"
