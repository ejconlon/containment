#!/bin/bash

set -euxo pipefail

: "${ROLES?}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

IFS=" "
for ROLE in ${ROLES}
do
  /usr/local/bin/ansible-playbook -i "localhost," -c local ${DIR}/../roles/${ROLE}/tasks.yml
done
