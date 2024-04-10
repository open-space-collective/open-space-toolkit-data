# Apache License 2.0

FROM python:3.11

LABEL maintainer="kyle.cochran@loftorbital.com"

RUN apt update && apt install -y vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip install durations

# Set the environment variable to not write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
