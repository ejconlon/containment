#!/bin/bash

# Run a container as built

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"

docker run -P ${ORG}/${IMAGE}
