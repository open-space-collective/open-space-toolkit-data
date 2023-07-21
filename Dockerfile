# Apache License 2.0

FROM python:3.11

LABEL maintainer="kyle.cochran@loftorbital.com"

RUN apt update && apt install -y vim
