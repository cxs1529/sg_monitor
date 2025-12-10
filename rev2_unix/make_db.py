from ncmodules import files #, ncdata, df_html
import sgid_list as sg
# import pandas as pd
# import sqlite3 as sql
import os

# Update your parent directory and sg IDs in sgid_list.py
# Check the test flag in files.py: if test=True it will only process a few .nc files

# MAIN ------------------------------------------------------------------------------------------------------
def main():

    print(f"Listing .nc files for {sg.sgids} in {sg.sourceDir}")
    for id in sg.sgids:
        dir_path = os.path.join(sg.sourceDir, "sg" + id)
        print(dir_path)
        try:
            make_database(id, dir_path)
        except:
            print("ERROR parsing sg" + id)
           


# MAIN ------------------------------------------------------------------------------------------------------


def make_database(sgid, dir_path):

    dbname = sgid + ".db"
    logtable = "log_table"
    # get list of nc files in directory matching the glider id
    ncfiles_raw = files.list_ncdir(dir_path, sgid)    

    # filter files already processed in database
    ncfile_list = files.get_files2process(ncfiles_raw, dbname, logtable)
    print("=====================")
    print(f">> {len(ncfile_list)} files to process")

    if files.process_directory(ncfile_list, dbname, logtable) != None:
        print(f"Files processed and stored in {dbname}")

    # read values from database
    df = files.read_database(dbname, logtable, "descending")
    # pd.set_option('display.max_columns', None)
    print(df)

    # print("Dataframe keys:")
    # print(df.keys())   

    # # access each column
    # for col in df.itertuples():
    #     print(f"Dive: {col.dive} DAC: {col.dac_velocity}")









# Entry point main ------------------------------------------------------------
if __name__ == "__main__":
    main()