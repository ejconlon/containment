ARG ORG
FROM $ORG/supervisor
COPY util/playbook.sh /context/util/playbook.sh
COPY roles/luigi /context/roles/luigi
COPY roles/clean /context/roles/clean
RUN ROLES="luigi clean" /context/util/playbook.sh && rm -rf /context
EXPOSE 8990
