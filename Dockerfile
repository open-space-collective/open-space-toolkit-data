# Apache License 2.0

ARG BASE_IMAGE_VERSION="latest"

#FROM openspacecollective/open-space-toolkit-base:${BASE_IMAGE_VERSION}
FROM python:3.11

LABEL maintainer="kyle.cochran@loftorbital.com"

RUN apt update && apt install -y vim
