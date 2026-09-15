# USER INPUT: SELECT DIRECTORIES TO COPY AND REPLACE
# ---------------------------------------------------------------------------
test = False
# ---------------------------------------------------------------------------
src = "static_website"
if test:
    dst1 = "/phoddat/share/phod/goos/gliders/monitoring_test/static_website2" # use this for testing in a separate directory not mirrored
else:
    dst2 = "/phoddat/share/phod/goos/gliders/sg_monitor/dashboard"
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

if test:
    copy_directory_replacing_existing(src, dst1)
else:
    copy_directory_replacing_existing(src, dst2)



