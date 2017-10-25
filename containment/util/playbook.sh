#!/bin/bash

set -euxo pipefail

: "${ROLES?}"
: "${VARS?}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

IFS=" "
for ROLE in ${ROLES}
do
  ROLE_VARS=$(echo ${VARS} | jq -r ".${ROLE} // {}")
  /usr/local/bin/ansible-playbook -i "localhost," -c local --extra-vars "${ROLE_VARS}" ${DIR}/../roles/${ROLE}/tasks.yml
done
