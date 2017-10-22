#!/bin/bash

# Build a container from ansible roles.

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"
: "${ROLES?}"

CWD="$(pwd)"

docker run -v ${CWD}:/repo -e ROLES="${ROLES}" ${ORG}/base \
  bash /repo/containment/util/playbook.sh

# Gets last executed container. Not safe on busy systems...
CONTAINER_ID="$(docker ps -lq)"

docker commit ${CONTAINER_ID} ${ORG}/${IMAGE}
