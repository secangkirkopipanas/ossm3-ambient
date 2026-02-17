#!/bin/bash

# Define available services and registry
REGISTRY="quay.io/rh_rh"
SERVICES=("user" "order" "product")
PLATFORM="linux/amd64"
SOURCE_DIR="src"

BASEDIR=$(dirname "$0")

usage() {
    echo "Usage: $0 [service_name | all]"
    echo "Available services: ${SERVICES[*]}"
    exit 1
}

# Check if a parameter was provided
if [ -z "$1" ]; then
    usage
fi

build_and_push() {
    local service=$1
    local image_name="${REGISTRY}/ossm3-${service}:latest"
    local context_dir="${BASEDIR}/${SOURCE_DIR}/${service}/"

    echo "-------------------------------------------------------"
    echo "> Processing: $service"
    echo "-------------------------------------------------------"

    echo "> Building $service image..."
    if podman build --platform ${PLATFORM} -t "$image_name" -f "${BASEDIR}/${SOURCE_DIR}/Containerfile" "$context_dir"; then
        echo "> Pushing $service image..."
        podman push "$image_name"
    else
        echo "Error: Build failed for $service"
        exit 1
    fi
}

# Logic to handle "all" or specific service
if [ "$1" == "all" ]; then
    for svc in "${SERVICES[@]}"; do
        build_and_push "$svc"
    done
else
    # Check if the requested service is in our list
    if [[ " ${SERVICES[*]} " =~ " $1 " ]]; then
        build_and_push "$1"
    else
        echo "Error: Service '$1' not found."
        usage
    fi
fi

echo -e "\n> Done!"