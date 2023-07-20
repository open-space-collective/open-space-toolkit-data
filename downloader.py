from datetime import datetime, timezone, timedelta
import json
import filecmp


def update(descriptor):
    
        from urllib import request
        from pathlib import Path

        data_folder = Path("data") / Path(descriptor["path"])
        filename_next = descriptor["filename"] + ".next"
        response = request.urlretrieve(descriptor["remote_sources"][0]["url"], data_folder / filename_next)

        # TODO: if download fails, try next remote source
        current_file = data_folder / descriptor["filename"]

        new_file = data_folder / filename_next

        # file diff to see if it has actually changed
        if current_file.exists():
            # already exists but has not changed
            if filecmp.cmp(current_file, new_file):
                new_file.unlink()
                print(f"No changes detected in {descriptor['filename']}")
            else:
                current_file.unlink()
                new_file.rename(current_file)
                print(f"Changes detected in { descriptor['filename']}. Updated file.")

        else:
            new_file.rename(current_file)
            print(f"{descriptor['filename']} was not present. Downloaded new copy.")

        # update manifest
        descriptor["last_update_check"] = datetime.now(timezone.utc).isoformat()
        descriptor["next_update_check"] = (datetime.now(timezone.utc) + timedelta(seconds=descriptor["check_frequency_s"])).isoformat()

        return descriptor


with open("manifest.json") as manifest_file:
    manifest = json.load(manifest_file)

for resource, descriptor in manifest.items():

    next_update_check_dt = datetime.fromisoformat(descriptor["next_update_check"])

    if next_update_check_dt < datetime.now(timezone.utc):
        
        print(f"Fetching {resource} to check for updates...")
        manifest[resource] = update(descriptor)

    else:
        print(f"Not checking {resource}.")
        print(f"  > Next check in {(next_update_check_dt - datetime.now(timezone.utc))}.")


with open("manifest.json", "w") as manifest_file:
    json.dump(manifest, manifest_file, indent=4)
