#!/bin/bash

# Run a given command in the built container

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"

CWD="$(pwd)"

if [[ $# -eq 0 ]]; then
  COMMAND="bash"
else
  # TODO handle quoting...
  COMMAND="$@"
fi

docker run -it -v ${CWD}/..:/context -P ${ORG}/${IMAGE} ${COMMAND}
