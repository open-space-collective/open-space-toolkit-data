# Apache License 2.0

import sys
from datetime import datetime, timezone, timedelta
import json
import filecmp
import tarfile
from urllib import request
from pathlib import Path
import shutil
from durations import Duration


def set_update_timestamps(descriptor: dict, updated: bool):
    '''
        Increment the `next_update_check` timestamp in the descriptor by it's `check_frequency`.

        Returns the updated descriptor.
    '''
    # set latest update time to now if updated
    if updated:
        descriptor["last_update"] = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "")
        )

    # increment next check time by check_frequency
    duration_td = timedelta(
        seconds=Duration(descriptor["check_frequency"]).to_seconds()
    )
    descriptor["next_update_check"] = (
        (datetime.now(timezone.utc) + duration_td).isoformat().replace("+00:00", "")
    )

    return descriptor


def download_check_and_update(descriptor: dict) -> dict:
    '''
        Download the resource described in `descriptor`. 

        If another version of this file already exists locally, determine if the newly downloaded file is different and update accordingly.

        Returns the updated descriptor.
    '''
    data_folder = Path("data") / Path(descriptor["path"])

    # Create data folder if it doesn't exist
    data_folder.mkdir(exist_ok=True, parents=True)

    staging_folder = data_folder / Path("next")

    # Create staging folder if it doesn't exist
    staging_folder.mkdir(exist_ok=True)

    filenames = (
        descriptor["filenames"]
        if type(descriptor["filenames"]) == list
        else [descriptor["filenames"]]
    )

    # TODO: if download fails, try next remote source
    remote_source = descriptor["remote_sources"][0]

    download_filename = remote_source["url"].split("/")[-1]
    response = request.urlretrieve(
        remote_source["url"], staging_folder / download_filename
    )

    if "needs_unpack" in remote_source.keys() and remote_source["needs_unpack"] == True:
        # Decompress the file
        unpack(staging_folder / download_filename)

        # Bring all sub files to root of staging directory
        flatten(staging_folder)

    # Compare files to assess updates
    updated = False

    for filename in filenames:
        updated = updated or compare_files_and_update(
            data_folder, staging_folder, filename
        )

    # Remove staging folder
    shutil.rmtree(staging_folder)

    # Log the update time and set next update check time
    descriptor = set_update_timestamps(descriptor, updated)

    return descriptor


def compare_files_and_update(current_dir, new_dir, filename):
    '''
        Compare two files with the same name in different directories.

        If there are differences, move the file from `new_dir` to `current_dir` and return True.
    '''
    current_file = current_dir / filename
    new_file = new_dir / filename

    # File diff to see if it has actually changed. Update if so.
    if current_file.exists():
        if filecmp.cmp(current_file, new_file):
            new_file.unlink()
            print(f"No changes detected in {filename}")
            return False
        else:
            current_file.unlink()
            new_file.rename(current_file)
            print(f"Changes detected in {filename}. Updated file.")
            return True

    else:
        new_file.rename(current_file)
        print(f"{filename} was not present. Downloaded new copy.")
        return True


def unpack(compressed_file):
    tar = tarfile.open(compressed_file)
    tar.extractall(compressed_file.parent)
    tar.close()


def flatten(root_directory):
    '''
        Move all files in subdirectories of `root_directory` to the root of `root_directory`.
    '''
    all_subfiles = [
        path_object
        for path_object in root_directory.rglob("*")
        if path_object.is_file()
    ]

    for file in all_subfiles:
        new_path = root_directory / file.name
        file.rename(new_path)


def determine_data_to_update(manifest) -> list[str]:
    '''
        Loop through the manifest entries and determine if the update frequency
        has been reached for any data file.

        If a force_update_pattern is provided, return any data entries with a name containing that pattern.

        Returns a list of data entries to check for updates.
    '''

    files_to_fetch = []

    for resource, descriptor in manifest.items():

        if resource == "manifest":
            continue

        # The time at which we have planned to check for updates on this data.
        next_update_check_dt = datetime.fromisoformat(descriptor["next_update_check"])

        if (
            next_update_check_dt.replace(tzinfo=timezone.utc)
            < datetime.now(timezone.utc)
        ):
            files_to_fetch.append(resource)

    return files_to_fetch
 
def update_resources(manifest: dict, resources_to_update: list[str]) -> dict:
    '''
        Fetch all resources in resources_to_update. These must be keys of `manifest`.

        Update any resources that have changes.
    '''

    if not set(resources_to_update).issubset(set(manifest.keys())):
        raise ValueError("The resource to update must match a key in the manifest.")

    for resource_name in manifest.keys():
        if resource_name == "manifest":
            continue
        if resource_name in resources_to_update:
            print(f"Fetching {resource_name} to check for updates...")
            manifest[resource_name] = download_check_and_update(manifest[resource_name])

        else:
            next_update_check_dt = datetime.fromisoformat(
                manifest[resource_name]["next_update_check"]
            )

            print(f"Not checking {resource_name}.")
            print(
                f"  > Next check in {(next_update_check_dt.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc))}."
            )

    return manifest
    
def global_update_frequency_reached(manifest: dict) -> bool:
    # Use manifest check frequency as a global throttle on updating.
    manifest_next_update_check_dt = datetime.fromisoformat(
        manifest["manifest"]["next_update_check"]
    ).replace(tzinfo=timezone.utc)

    return manifest_next_update_check_dt < datetime.now(timezone.utc)

def log_manifest_update(manifest: dict) -> dict:
    # Log an update for the manifest itself.
    print("Logging manifest update.")
    manifest["manifest"] = set_update_timestamps(
        descriptor=manifest["manifest"], updated=True
    )
    return manifest

def main():

    force_update_pattern = sys.argv[1] if len(sys.argv) > 1 else None

    with open("data/manifest.json") as manifest_file:
        manifest = json.load(manifest_file)

    if not global_update_frequency_reached(manifest):
        print("Global update frequency not yet reached. Nothing to do.")
        return

    resources_to_update: list[str] = determine_data_to_update(manifest)
    manifest: dict = update_resources(manifest, resources_to_update)

    manifest: dict = log_manifest_update(manifest)

    with open("data/manifest.json", "w") as manifest_file:
        json.dump(manifest, manifest_file, indent=4)


if __name__ == "__main__":
    main()
