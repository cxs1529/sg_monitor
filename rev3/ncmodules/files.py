import os
import sqlite3 as sql
from ncmodules import ncdata
import pandas as pd
import traceback
import json

# test only N files
test = False # False: process all .nc in dir / True: process only first nfiles
nfiles = 10 # no. of .nc files to process

def list_ncdir(dir, sgid):
    print("=====================")
    print("Scanning directory: " + dir)
    
    ncpath_list = []
    if os.path.isdir(dir) == True: 
        filelist = os.listdir(dir)        
        index = 0
        for file in filelist:
            if test == True:
                if index >= nfiles:
                    break
            fullpath = os.path.join(dir,file)

            if os.path.isfile(fullpath) == True:
                if file.endswith(".nc") == True:
                    print("Found netCDF file: ", file)    
                    if file.startswith("p"+ sgid) == True:               
                        ncpath_list.append(fullpath)
                        index = index + 1
                    else:
                        print("Glider ID doesn't match " + sgid + "!")
                else:
                    print(fullpath + " is not an .nc file!")            
            else:
                print(fullpath + " is not a file")
    else:
        print(dir + " is not a directory!")

    return ncpath_list

def get_files2process(ncfile_list, dbname, logtable):
    if os.path.isfile(dbname) == True:
        print("=====================")
        print(f">> Database {dbname} found!")
        dbcon = sql.connect(dbname)
        dbcursor = dbcon.cursor()
        dbcursor.execute(f"SELECT filePath from {logtable}")
        items = dbcursor.fetchall()   

        print("=====================")     
        print(">> Files in database:")  
        dbfiles = {f[0] for f in items}
        # dbfiles = []
        # for f in items:           
        #     print(f[0])
        #     dbfiles.append(f[0])

        print("=====================")
        print(">> Filtering out processed files:") 
        newfiles = [f for f in ncfile_list if f not in dbfiles]
        # newfiles = []
        # for f in ncfile_list:
        #     if f in dbfiles:
        #         print(f"{f} already processed")
        #     else:
        #         newfiles.append(f)   
        #         print(f"{f} not processed")         

        return newfiles
    else:
        print("=====================")
        print(f">> {dbname} database NOT found!")
        return ncfile_list


# Handles the formatting and saving of a single dive's JSON file.
def save_dive_json(record, sgid, dive_num, ncfile):

    json_dir = os.path.join("static", "json")
    os.makedirs(json_dir, exist_ok=True)
    
    json_filename = os.path.join(json_dir, f"sg{sgid}{dive_num:04d}.json")
    
    print(f"  -> Exporting {ncfile} to {json_filename}...")
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(record, jf, indent=4)


def process_directory(ncfile_list, dbname, logtable, sgid):
    if len(ncfile_list) > 0:
        df = pd.DataFrame()
        idx = 0
        
        for ncfile in ncfile_list:
            try:
                # Unpack BOTH dictionaries from the single file read to be more efficient
                thisdive_dict, record = ncdata.process_netcdf(ncfile)
                
                # 1. Update dataframe for SQLite
                thisdive_df = pd.DataFrame(thisdive_dict, index = [idx])
                thisdive_df["filePath"] = ncfile
                df = pd.concat([df, thisdive_df], sort=False)
                
                # 2. Export JSON immediately from memory
                dive_num = int(thisdive_dict.get('dive', 0))
                save_dive_json(record, sgid, dive_num, ncfile)
                    
                idx = idx + 1
            except Exception as e:
                print(f">> Skipping {ncfile}. Error: {e}")
                traceback.print_exc()

        if not df.empty:
            conn = sql.connect(dbname)
            rows = df.to_sql(logtable, conn, if_exists='append', index=False)
            conn.close()
            return rows
        else:
            print(f">> No valid data extracted to create database for {dbname}.")
            return None

# if len(ncfile_list) > 0:
#     df = pd.DataFrame()
#     idx = 0
#     for ncfile in ncfile_list:
#         try:
#             thisdive_dict = ncdata.process_netcdf(ncfile)
#             thisdive_df = pd.DataFrame(thisdive_dict, index = [idx])
#             thisdive_df["filePath"] = ncfile
#             df = pd.concat([df, thisdive_df], sort=False)
#             idx = idx + 1
#         except Exception as e:
#             # Stop skipping errors to see what failed in the console
#             print(f">> Skipping {ncfile}. Error: {e}")
#             traceback.print_exc()

#     # Prevent empty dataframes from crashing SQLite creation
#     if not df.empty:
#         conn = sql.connect(dbname)
#         rows = df.to_sql(logtable, conn, if_exists='append', index=False)
#         conn.close()
#         return rows
#     else:
#         print(f">> No valid data extracted to create database for {dbname}.")
#         return None


def read_database(dbname, logtable, order):
    print("=====================")
    print(f">> Reading {dbname}\n")
    conn = sql.connect(dbname) 
    if order == "descending":
        df_read = pd.read_sql_query(f"SELECT * FROM {logtable} ORDER BY dive DESC;", conn)
    else:
        df_read = pd.read_sql_query(f"SELECT * FROM {logtable} ORDER BY dive ASC;", conn)
    conn.close()    

    df = df_read.fillna(-9.999)
    return df


# Export netcdf as json file and store in static/json directory
# Exports all parameters from the source .nc files to individual JSON files
def export_to_json(df, sgid):
    
    json_dir = os.path.join("static", "json")
    os.makedirs(json_dir, exist_ok=True) 
    
    try:
        count = 0
        skipped = 0
        
        for row in df.itertuples(index=False):
            dive_num = int(getattr(row, 'dive', 0))
            ncfile = getattr(row, 'filePath', None)
            
            # if not an .nc file skip
            if pd.isna(ncfile) or not os.path.isfile(str(ncfile)):
                continue
            # file path
            json_filename = os.path.join(json_dir, f"sg{sgid}{dive_num:04d}.json")

            # skip if file already exists
            if os.path.exists(json_filename):
                skipped += 1
                continue
            
            print(f"  -> Exporting {ncfile} to {json_filename}...")
            # get all variables in .nc file
            record = ncdata.get_all_variables(str(ncfile))
            # write json file
            with open(json_filename, "w", encoding="utf-8") as jf:
                json.dump(record, jf, indent=4)
            
            count += 1
                
        print(f">> Generated {count} new JSON files for SG{sgid} in {json_dir} ({skipped} existing skipped)")
    except Exception as e:
        print(f">> Error generating JSON files for SG{sgid}: {e}")
        traceback.print_exc()