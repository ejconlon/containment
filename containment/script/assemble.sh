#!/bin/bash

# Build a container from ansible roles.

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"
: "${ROLES?}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

docker run -v ${DIR}/..:/context -e ROLES="${ROLES}" ${ORG}/base \
  bash /context/util/playbook.sh

# Gets last executed container. Not safe on busy systems...
CONTAINER_ID="$(docker ps -lq)"

docker commit ${CONTAINER_ID} ${ORG}/${IMAGE}
