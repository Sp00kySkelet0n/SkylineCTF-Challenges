#!/bin/bash

# Build the wizard image if it doesn't exist (or force update with --build)
if [[ "$(docker images -q skyline-wizard 2> /dev/null)" == "" ]] || [[ "$1" == "--build" ]]; then
    echo "🏗️  Construction de l'image Docker du wizard..."
    docker build -t skyline-wizard -f Dockerfile.wizard .
fi

echo "🧙‍♂️  Lancement du Wizard..."

# Run the container
# -v $(pwd):/app : Mount current directory to /app
# -it : Interactive mode
# --rm : Remove container after exit
docker run -it --rm \
    -e PYTHONDONTWRITEBYTECODE=1 \
    -v "$(pwd):/app" \
    -v "${HOME}/.gitconfig:/root/.gitconfig:ro" \
    skyline-wizard
