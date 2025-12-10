from ncmodules import files, ncdata


dir_path = "C:\\Users\\christian.saiz\\Documents\\0_NOAA\\1_NOAA_work\\2_GLIDERS\\2025\\piloting\\NC\\683\\p6830520.nc"


thisdive_dict = ncdata.process_netcdf(dir_path)

for key in thisdive_dict:
    print(key, " : ", thisdive_dict[key])