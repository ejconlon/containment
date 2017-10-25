ARG ORG
FROM amazonlinux:latest
RUN yum -y update && \
    yum -y install \
      jq \
      python36 \
      python36-pip && \
    pip-3.6 install ansible
