#!/bin/bash

# Run a given command in the built container

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"

CWD="$(pwd)"

docker run -it -v ${CWD}:/repo -P ${ORG}/${IMAGE} $@
