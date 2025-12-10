# USER INPUT: SELECT DIRECTORIES TO COPY AND REPLACE
# ---------------------------------------------------------------------------
src = "static_website"
#dst = "/phoddat/share/phod/goos/gliders/monitoring_test/static_website" # use this for testing in a separate directory not mirrored
dst = "/phoddat/share/phod/goos/gliders/sg_monitor/dashboard"

# ---------------------------------------------------------------------------


import shutil
import os


def copy_directory_replacing_existing(source_dir, destination_dir):
    """
    Copies a source directory to a destination directory, replacing the 
    destination directory if it already exists.

    Args:
        source_dir (str): The path to the source directory.
        destination_dir (str): The path to the destination directory.
    """
    if os.path.exists(destination_dir):
        print(f"Removing existing directory: {destination_dir}")
        shutil.rmtree(destination_dir)
    
    print(f"Copying '{source_dir}' to '{destination_dir}'")
    shutil.copytree(source_dir, destination_dir)
    print("Copy completed.")



# ---------------------------------------------------------------------------

copy_directory_replacing_existing(src, dst)



