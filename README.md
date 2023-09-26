# Open Space Toolkit ▸ Data

[![Sync](https://github.com/open-space-collective/open-space-toolkit-data/actions/workflows/scheduled-sync.yml/badge.svg?branch=main)](https://github.com/open-space-collective/open-space-toolkit-data/actions/workflows/scheduled-sync.yml)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Data for the space environment automatically fetched using Github Actions.

## Getting Started

You can clone this repository and run the data fetching yourself. [*requires Docker*].

```bash
make pull-data
```

However since the data is update periodically on the remote, a regular 'ole `git pull` should be sufficient to keep you updated!

If you really want to see it in action, feel free to delete the entire `data` directory and run `make pull-data` again.

## Setup

### Development Environment

Using [Docker](https://www.docker.com) for development is recommended, to simplify the installation of the necessary build tools and dependencies.
Instructions on how to install Docker are available [here](https://docs.docker.com/install/).

To start the development environment:

```bash
make start-development
```

## Adding New Data
TODO: explain manifest, compression, and multiple files/data sources
TODO: mention how to add with git LFS, use `du -sh` to check size. > 1MB should probably use LFS
- You must create any neccesary subdirectories yourself
- Run `make pull-data` to verify that your manifest configuration is correct.

## Contribution

Contributions are more than welcome!

Please read our [contributing guide](CONTRIBUTING.md) to learn about our development process, how to propose fixes and improvements, and how to build and test the code.

## Special Thanks

[![Loft Orbital](https://github.com/open-space-collective/open-space-toolkit/blob/main/assets/thanks/loft_orbital.png)](https://www.loftorbital.com/)

## License

Apache License 2.0
