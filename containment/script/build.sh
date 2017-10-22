#!/bin/bash

# Build a container from a Dockerfile.

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"

CONTEXT="containment"
DOCKERFILE="${CONTEXT}/images/${IMAGE}/Dockerfile"
docker build --build-arg ORG=${ORG} -t ${ORG}/${IMAGE} -f ${DOCKERFILE} ${CONTEXT}
