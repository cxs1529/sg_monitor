import os
import sqlite3 as sql
from ncmodules import ncdata
import pandas as pd

# dirpath = "C:\\Users\\christian.saiz\\Documents\\0_NOAA\\1_NOAA_work\\2_GLIDERS\\2025\\piloting\\668"

# test only N files
test = False # False: process all .nc in dir / True: process only first nfiles
nfiles = 10 # no. of .nc files to process

def list_ncdir(dir, sgid):
    print("=====================")
    print("Scanning directory: " + dir)
    
    ncpath_list = []
    # Check if the path is a valid directory
    if os.path.isdir(dir) == True: 
        # list dir files
        filelist = os.listdir(dir)        

        index = 0
        # if dir is valid, loop throgh list of files and create full absolute path       
        for file in filelist:
            # if run is a test loop nfiles times only
            if test == True:
                if index >= nfiles:
                    break
            # create full path based on OS
            fullpath = os.path.join(dir,file)

            if os.path.isfile(fullpath) == True:
                # check that the file is netcdf
                if file.endswith(".nc") == True:
                    print("Found netCDF file: ", file)    
                    # check that is the correct glider ID
                    if file.startswith("p"+ sgid) == True:               
                        ncpath_list.append(fullpath)
                        index = index + 1
                    else:
                        print("Glider ID doesn't match " + sgid + "!")
                # if not a netcdf file, print warning
                else:
                    print(fullpath + " is not an .nc file!")            
            # if not a file, print warning
            else:
                print(fullpath + " is not a file")
    
    # if not a directory, print warning
    else:
        print(dir + " is not a directory!")

    # return complete dataframe of dir data
    return ncpath_list



def get_files2process(ncfile_list, dbname, logtable):
    # check if db exists and return list of files not in the table
    if os.path.isfile(dbname) == True:
        print("=====================")
        print(f">> Database {dbname} found!")
        # get list of files already processed and in database
        dbcon = sql.connect(dbname)
        dbcursor = dbcon.cursor()
        dbcursor.execute(f"SELECT filePath from {logtable}")
        items = dbcursor.fetchall()   
        print("=====================")     
        print(">> Files in database:")  
        dbfiles = []
        for f in items:           
            print(f[0])
            dbfiles.append(f[0])

        # compare list and create list with files not processed
        print("=====================")
        print(">> Filtering out processed files:") 
        newfiles = []
        for f in ncfile_list:
            if f in dbfiles:
                print(f"{f} already processed")
            else:
                newfiles.append(f)   
                print(f"{f} not processed")         

        return newfiles
    
    # else return same input list
    else:
        print("=====================")
        print(f">> {dbname} database NOT found!")
        return ncfile_list


def process_directory(ncfile_list, dbname, logtable):
    if len(ncfile_list) > 0:
        # start empty dataframe
        df = pd.DataFrame()
        # loop through nc files and process each
        idx = 0
        for ncfile in ncfile_list:   
            # get dictionary from ncfile     
            thisdive_dict = ncdata.process_netcdf(ncfile)
            #ncdata.print_dictionary(thisdive_dict)
            # create dataframe from dictonary
            thisdive_df = pd.DataFrame(thisdive_dict, index = [idx])
            # add column with filepath
            thisdive_df["filePath"] = ncfile
            # append to main dataframe 
            df = pd.concat([df, thisdive_df])
            idx = idx + 1

        # Store values in database
        conn = sql.connect(dbname)
        rows = df.to_sql(logtable, conn, if_exists='append', index=False)
        conn.close()

        return rows

# returns database table as dataframe ordered in ascending or descending order by dive number
def read_database(dbname, logtable, order):
    print("=====================")
    print(f">> Displaying {dbname} values:\n")
    conn = sql.connect(dbname) 
    if order == "descending":
        df_read = pd.read_sql_query(f"SELECT * FROM {logtable} ORDER BY dive DESC;", conn)
    else:
        df_read = pd.read_sql_query(f"SELECT * FROM {logtable} ORDER BY dive ASC;", conn)
    conn.close()    

    # replace NaN with a float so it doesn't crash casting when creating html
    df = df_read.fillna(-9.999)

    return df