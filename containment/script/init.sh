#!/bin/bash

# Initialize and build some basic containers.

set -euxo pipefail

: "${ORG?}"

docker pull amazonlinux

IMAGE=base ./containment/script/build.sh

IMAGE=buildenv ./containment/script/build.sh

IMAGE=supervisor ./containment/script/build.sh
