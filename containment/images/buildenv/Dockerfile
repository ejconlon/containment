ARG ORG
FROM $ORG/base
COPY util/playbook.sh /context/util/playbook.sh
COPY roles/buildenv /context/roles/buildenv
COPY roles/clean /context/roles/clean
RUN ROLES="buildenv clean" /context/util/playbook.sh && rm -rf /context
