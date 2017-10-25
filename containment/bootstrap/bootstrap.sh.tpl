#!/bin/bash

set -eEuxo pipefail

HEALTHZ=/var/opt/healthz
STATE=${HEALTHZ}/state

mkdir -p $HEALTHZ

function error() {
    echo "error" >> $STATE
}

trap error ERR

echo "syncing" >> $STATE

aws s3 sync _SOURCE_ /context

echo "installing" >> $STATE

sudo yum -y update
sudo yum -y install jq python36 python36-pip
pip-3.6 install ansible

echo "configuring" >> $STATE

ROLES='_ROLES_' VARS='_VARS_' bash /context/util/playbook.sh

echo "ready" >> $STATE
