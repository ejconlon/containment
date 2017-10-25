#!/bin/bash

# Build a container from a Dockerfile.

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"
: "${TYPE?}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

CONTEXT="${DIR}/.."

DOCKERFILE="${CONTEXT}/${TYPE}/${IMAGE}/Dockerfile"

docker build --build-arg ORG=${ORG} -t ${ORG}/${IMAGE} -f ${DOCKERFILE} ${CONTEXT}
