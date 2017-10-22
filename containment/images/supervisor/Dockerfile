ARG ORG
FROM $ORG/base
COPY util/playbook.sh /context/util/playbook.sh
COPY roles/supervisor /context/roles/supervisor
COPY roles/clean /context/roles/clean
RUN ROLES="supervisor clean" /context/util/playbook.sh && rm -rf /context
EXPOSE 9001
CMD supervisord -c /etc/supervisor/supervisord.conf
