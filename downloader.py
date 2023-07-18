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
                print("No changes detected in " + descriptor["filename"])
            else:
                current_file.unlink()
                new_file.rename(current_file)
                print("Updated " + descriptor["filename"])

        else:
            new_file.rename(current_file)
            print("Downloaded new file" + descriptor["filename"])

        # update manifest
        descriptor["last_update"] = datetime.now(timezone.utc).isoformat()
        descriptor["next_update"] = (datetime.now(timezone.utc) + timedelta(seconds=descriptor["update_frequency_s"])).isoformat()

        return descriptor


with open("manifest.json") as manifest_file:
    manifest = json.load(manifest_file)

for resource, descriptor in manifest.items():

    if datetime.fromisoformat(descriptor["next_update"]) < datetime.now(timezone.utc):
        
        print("Downloading " + resource + "...")
        manifest[resource] = update(descriptor)

    else:
        print("Skipping " + resource + "...")


with open("manifest.json", "w") as manifest_file:
    json.dump(manifest, manifest_file, indent=4)
