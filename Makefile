# Apache License 2.0

build:

	@ echo "Building development image..."

	docker build \
		--file="$(CURDIR)/Dockerfile" \
		--tag="open-space-toolkit-data:latest" \
		"$(CURDIR)"

.PHONY: build

start-development dev: build
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


determine-updates: build
	@ echo "Determining updates..."

	docker run \
		--rm \
		--privileged \
		--volume="$(CURDIR):/app:delegated" \
		--workdir="/app" \
		"open-space-toolkit-data:latest" \
		/bin/bash -c "python3.11 -c \"from downloader import determine_updates; print(','.join(determine_updates()))\" | tr ',' '\n'"

.PHONY: determine-updates


pull-data: build
	@ echo "Pulling new data from remotes..."

	docker run \
		--rm \
		--privileged \
		--volume="$(CURDIR):/app:delegated" \
		--workdir="/app" \
		"open-space-toolkit-data:latest" \
		/bin/bash -c "python3.11 /app/downloader.py $(FORCE)"

.PHONY: pull-data
