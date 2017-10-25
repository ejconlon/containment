#!/bin/bash

# Run a given command in the built container

set -euxo pipefail

: "${ORG?}"
: "${IMAGE?}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

CONTEXT="${DIR}/.."

if [[ $# -eq 0 ]]; then
  COMMAND="bash"
else
  # TODO handle quoting...
  COMMAND="$@"
fi

docker run -it -v ${CONTEXT}:/context -P ${ORG}/${IMAGE} ${COMMAND}
