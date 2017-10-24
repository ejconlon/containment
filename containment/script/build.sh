#!/bin/bash

# Build a container from a Dockerfile.

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"
: "${TYPE?}"

CONTEXT="containment"
DOCKERFILE="${CONTEXT}/${TYPE}/${IMAGE}/Dockerfile"
docker build --build-arg ORG=${ORG} -t ${ORG}/${IMAGE} -f ${DOCKERFILE} ${CONTEXT}
