from datetime import datetime, timezone, timedelta
import json
import filecmp
import tarfile
from urllib import request
from pathlib import Path
import shutil

def download_check_and_update(descriptor):

        data_folder = Path("data") / Path(descriptor["path"])

        # create data folder if it doesn't exist
        data_folder.mkdir(exist_ok=True, parents=True)

        staging_folder = data_folder / Path("next")

        # create staging folder if it doesn't exist
        staging_folder.mkdir(exist_ok=True)

        filenames = descriptor["filenames"] if type(descriptor["filenames"]) == list else [descriptor["filenames"]]

        # TODO: if download fails, try next remote source
        remote_source = descriptor["remote_sources"][0]

        download_filename = remote_source["url"].split("/")[-1]
        response = request.urlretrieve(remote_source["url"], staging_folder / download_filename)

        if "needs_unpack" in remote_source.keys() and remote_source["needs_unpack"] == True:
            # decompress the file
            unpack(staging_folder / download_filename)

            # bring all sub files to root of staging directory 
            flatten(staging_folder)
            
        # Compare files to assess updates
        for filename in filenames:
            compare_files_and_update(data_folder, staging_folder, filename)

        # remove staging folder
        shutil.rmtree(staging_folder)

        # update manifest
        descriptor["last_update_check"] = datetime.now(timezone.utc).isoformat()
        descriptor["next_update_check"] = (datetime.now(timezone.utc) + timedelta(seconds=descriptor["check_frequency_s"])).isoformat()

        return descriptor

def compare_files_and_update(current_dir, new_dir, filename):
    current_file = current_dir / filename
    new_file = new_dir / filename

    # file diff to see if it has actually changed. Update if so.
    if current_file.exists():
        if filecmp.cmp(current_file, new_file):
            new_file.unlink()
            print(f"No changes detected in {descriptor['filenames']}")
        else:
            current_file.unlink()
            new_file.rename(current_file)
            print(f"Changes detected in { descriptor['filenames']}. Updated file.")

    else:
        new_file.rename(current_file)
        print(f"{descriptor['filenames']} was not present. Downloaded new copy.")

def unpack(compressed_file):
    tar = tarfile.open(compressed_file)
    tar.extractall(compressed_file.parent)
    tar.close()

def flatten(root_directory):
    all_subfiles = [path_object for path_object in root_directory.rglob('*') if path_object.is_file()]

    for file in all_subfiles:
        new_path = root_directory / file.name
        file.rename(new_path)



##
## MAIN
##
with open("manifest.json") as manifest_file:
    manifest = json.load(manifest_file)

for resource, descriptor in manifest.items():

    next_update_check_dt = datetime.fromisoformat(descriptor["next_update_check"])

    if next_update_check_dt < datetime.now(timezone.utc):
        
        print(f"Fetching {resource} to check for updates...")
        manifest[resource] = download_check_and_update(descriptor)

    else:
        print(f"Not checking {resource}.")
        print(f"  > Next check in {(next_update_check_dt - datetime.now(timezone.utc))}.")


with open("manifest.json", "w") as manifest_file:
    json.dump(manifest, manifest_file, indent=4)
