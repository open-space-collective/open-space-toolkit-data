# Apache License 2.0

build:

	@ echo "Building development image..."

	docker build \
		--file="$(CURDIR)/Dockerfile" \
		--tag="open-space-toolkit-data:latest" \
		"$(CURDIR)"

.PHONY: build

start-development: build
	@ echo "Starting development environment..."

	docker run \
		-it \
		--rm \
		--privileged \
		--volume="$(CURDIR):/app:delegated" \
		--workdir="/app" \
		"open-space-toolkit-data:latest" \
		/bin/bash

.PHONY: start-development

pull-data: build
	@ echo "Pulling new data from remotes..."

	docker run \
		--rm \
		--privileged \
		--volume="$(CURDIR):/app:delegated" \
		--workdir="/app" \
		"open-space-toolkit-data:latest" \
		/bin/bash -c "python3.11 /app/downloader.py $(FORCE)"

.PHONY: start-development
