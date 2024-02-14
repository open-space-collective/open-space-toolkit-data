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

## How It Works

This repo contains a selection of data files intended for use with the Open Space Toolkit collection of libraries. All data is publicly available and comes from other sources, so OSTk Data simply acts as an aggregator for space environment data. This helps when the primary data sources might be flaky and separates some of the data update logic from the OSTk runtime environment.

All data is store in the aptly named `data` folder, and the structure mirrors that of OSTk Physics, where the data is used. There is also another file that is used for bookkeeping: `data/manifest.json`

Here is an example snippet:

```json
    "space-weather-CSSI": {
        "path": "environment/atmospheric/earth/CSSISpaceWeather",
        "filenames": "SW-Last5Years.csv",
        "remote_sources": [
            {
                "url": "https://celestrak.org/SpaceData/SW-Last5Years.csv"
            }
        ],
        "last_update": "2024-02-13T20:23:40.707671",
        "next_update_check": "2024-02-14T02:23:40.707740",
        "check_frequency": "6 hours"
    }
```

This file keeps track of a few things:

- which data we have [`space-weather-CSSI`]
- where it should be stored [`path`]
- when it was last updated [`last_update`]
- when we should next check for updates for each data file [`next_update_check`/`check_frequency`]
- primary sources for the data [`remote_sources`]

We use [github actions](https://docs.github.com/en/actions) to periodically check against this file and fetch new data from each individual data source if we think there might be updates (based on the `check_frequency`). If the file contents are indeed different from what is in the OSTk Data repo, we commit the new changes.

When running any Open Space Toolkit library, we can then target this repo to fetch necessary data files. Additionally, this allows OSTk to make smart fetching decisions at runtime by making use of the `manifest.json`. An OSTk instance can simply fetch the manifest file and compare with it's pre-existing manifest file to determine if the OSTk Data remote has any new data files. This can eliminate the need for unnecessary data fetching at runtime.

## Versioning

The OSTk Data repo acts as a GET-only REST API. It is versioned by using named git branches. Current versions are:

- V0 (ref: `main`)
- V1 (ref: `v1`)

And you can query data from different versions using URLs formatted in the following way:

`https://github.com/open-space-collective/open-space-toolkit-data/raw/<ref>/data/<data path>`

All versions contain the same data, the files are just organized differently.

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
