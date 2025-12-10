from ncmodules import files, ncdata, table_html
import pandas as pd
import sqlite3 as sql
import os

dir_path = "C:\\Users\\christian.saiz\\Documents\\0_NOAA\\1_NOAA_work\\2_GLIDERS\\2025\\piloting\\668"
sgid = "668"
dbname = sgid + ".db"
logtable = "log_table"

# Check the test flag in files.py: if test=True it will only process a few .nc files

# MAIN ------------------------------------------------------------------------------------------------------
def main():

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
    pd.set_option('display.max_columns', None)
    print(df)

    print("Dataframe keys:")
    print(df.keys())

    # df_html.convert_to_table(df)

    # print(df.dive[1], len(df))
    

    # # access each column
    # for col in df.itertuples():
    #     print(f"Dive: {col.dive} DAC: {col.dac_velocity}")
           


# MAIN ------------------------------------------------------------------------------------------------------












# Entry point main ------------------------------------------------------------
if __name__ == "__main__":
    main()