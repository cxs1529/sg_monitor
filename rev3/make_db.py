from ncmodules import files
import sgid_list as sg
import os

# Update your parent directory and sg IDs in sgid_list.py
# Check the test flag in files.py: if test=True it will only process a few .nc files

# MAIN ------------------------------------------------------------------------------------------------------
def main():

    print(f"Listing .nc files for {sg.sgids} in {sg.sourceDir}")
    for id in sg.sgids:
        # Check standard directory name first based on sgid_list.py comments (e.g., /649)
        dir_path = os.path.join(sg.sourceDir, id)
        
        # Fallback just in case they are actually prefixed with "sg" (e.g., /sg649)
        if not os.path.exists(dir_path):
            dir_path_alt = os.path.join(sg.sourceDir, "sg" + id)
            if os.path.exists(dir_path_alt):
                dir_path = dir_path_alt

        print(f"Looking in: {dir_path}")
        
        try:
            make_database(id, dir_path)
        except Exception as e:
            print(f"ERROR parsing sg{id}: {e}")
           

# MAIN ------------------------------------------------------------------------------------------------------


def make_database(sgid, dir_path):

    dbname = sgid + ".db"
    logtable = "log_table"
    # get list of nc files in directory matching the glider id
    ncfiles_raw = files.list_ncdir(dir_path, sgid)    

    # filter files already processed in database
    ncfile_list = files.get_files2process(ncfiles_raw, dbname, logtable)
    # Sort files ascending based on filename to ensure they are parsed/added in order
    ncfile_list = sorted(ncfile_list)
    
    print("=====================")
    print(f">> {len(ncfile_list)} files to process")

    if files.process_directory(ncfile_list, dbname, logtable, sgid) is not None:
            print(f"Files processed and stored in {dbname}")

    # read values from database (Check if DB exists to prevent crashes on empty runs)
    if os.path.exists(dbname):
        try:
            # read the database to verify it's ok
            df = files.read_database(dbname, logtable, "descending")
            print(f">> Verified {len(df)} total dives in {dbname}\n")
            print("**************************************************\n\n")

        except Exception as e:
            print(f"Database {dbname} exists but could not be read: {e}")
    else:
        print(f"Database {dbname} was not created (no valid files processed).")


# Entry point main ------------------------------------------------------------
if __name__ == "__main__":
    main()