import netCDF4 as nc 
import numpy as np
import pandas as pd
from datetime import datetime

# User input
timefilter = 1 # [sec] filter out values with an action time of less than timefiler

# prints a dictionary in a column
def print_dictionary(dict):    
    for var in dict:
        print(var, ":", dict[var])

# Returns distance over ground  in km and bearing between 2 gps positions as dd.ddd
def haversine(lat1,lon1,lat2,lon2):
    # distance between 2 positions
    lat1, lon1, lat2, lon2 = map(np.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])    
    dlon = lon2 - lon1
    dlat = lat2 - lat1    
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2    
    c = 2 * np.arcsin(np.sqrt(a))
    distance = 6378 * c # km
    # bearing between 2 positions
    y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    x = np.sin(dlon) * np.cos(lat2)
    heading = (np.arctan2(y,x) * 180/np.pi) % 360

    # return result as dictionary
    displacement = {"distance": distance, "heading" : heading}
    return displacement


# Extracts all variables from an open NetCDF dataset into a dictionary
def extract_all_variables(nc_obj):
    
    all_data = {}
    for var in nc_obj.variables:
        raw_val = nc_obj.variables[var][:]
        
        # Try decoding byte/char arrays into readable strings
        if raw_val.dtype.kind in ['S', 'U']:
            try:
                decoded = np.char.decode(raw_val, encoding='utf-8')
                # Join arrays of chars into a single string and strip whitespace
                all_data[var] = "".join(np.atleast_1d(decoded)).strip()
            except Exception:
                all_data[var] = raw_val.tolist()
        else:
            # Handle masked arrays by filling missing values (e.g. -9.999)
            if np.ma.isMaskedArray(raw_val):
                raw_val = raw_val.filled(-9.999)
            
            # Convert NumPy arrays to standard Python lists
            val_list = np.atleast_1d(raw_val).tolist()
            
            # Unbox single values for cleaner JSON
            if len(val_list) == 1:
                all_data[var] = val_list[0]
            else:
                all_data[var] = val_list
    return all_data




# Parse NetCDF file object and return relevant log parameters as a dictionary
def process_netcdf(ncfile):
    print("=====================")
    print("Processing netCDF file: " + ncfile)
    # open and read netcdf file
    ncdata = nc.Dataset(ncfile)

    # dive number
    log_dive = ncdata.variables["log_dive"][:].tolist()
    
    # time and position
    log_gps_lat = ncdata.variables["log_gps_lat"][:].tolist() # [GPS1 GPS2 GPS]
    log_gps_lon = ncdata.variables["log_gps_lon"][:].tolist()
    log_gps_time = ncdata.variables["log_gps_time"][:].tolist() # epoch times for gps1 gps2 gps
    
    # utc times conversion
    log_gps_time_utc = []
    for t in log_gps_time:    
        dt = datetime.utcfromtimestamp(t)
        dt_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        log_gps_time_utc.append(dt_str)
        
    # derived dive time
    glider_dive_time = log_gps_time[-1] - log_gps_time[-2] # time between last 2 gps fixes. Take into account time for maneuvers
    total_flight_time_s = ncdata.variables["total_flight_time_s"][:].tolist()
    
    # log_gps_lat and log_gps_lon are lists with [GPS1 GPS2 GPS] >> 1st-fix 2nd-fix --dive-- fix-post-dive > determine DOG with GPS2 and GPS
    displacement = haversine(float(log_gps_lat[1]), float(log_gps_lon[1]), float(log_gps_lat[2]), float(log_gps_lon[2])) # distance over ground [km] and bearing [deg]
    glider_dog = displacement["distance"]
    glider_hdg = displacement["heading"]
    glider_sog = glider_dog * 1000 / glider_dive_time # speed over ground [m/s]
    
    # sea currents
    depth_avg_curr_east = ncdata.variables["depth_avg_curr_east"][:].tolist() # in m/s
    depth_avg_curr_north = ncdata.variables["depth_avg_curr_north"][:].tolist()
    dac_velocity = np.hypot(depth_avg_curr_north,depth_avg_curr_east)
    dac_heading = (np.pi/2 - np.arctan2(depth_avg_curr_north, depth_avg_curr_east)) * 180.0 / np.pi

    surface_curr_east = ncdata.variables["surface_curr_east"][:].tolist() # in cm/s
    surface_curr_north = ncdata.variables["surface_curr_north"][:].tolist()
    surf_velocity = np.hypot(surface_curr_north, surface_curr_east) / 100.0 # in m/s
    surf_heading = (np.pi/2 - np.arctan2(surface_curr_north, surface_curr_east)) * 180.0 / np.pi

    # control parameters
    log_D_TGT = ncdata.variables["log_D_TGT"][:].tolist()
    log_D_ABORT = ncdata.variables["log_D_ABORT"][:].tolist()
    log_T_DIVE = ncdata.variables["log_T_DIVE"][:].tolist()
    log_T_MISSION = ncdata.variables["log_T_MISSION"][:].tolist()
    log_T_ABORT = ncdata.variables["log_T_ABORT"][:].tolist()
    
    # target control 
    log_HEADING = ncdata.variables["log_HEADING"][:].tolist()
    log_NAV_MODE = ncdata.variables["log_NAV_MODE"][:].tolist()
    log_TGT_NAME = np.char.decode(ncdata.variables["log_TGT_NAME"], encoding='utf-8')
    log_TGT_NAME = "".join(log_TGT_NAME)
    log_TGT_LATLONG = np.char.decode(ncdata.variables["log_TGT_LATLONG"], encoding='utf-8')
    log_TGT_LATLONG = "".join(log_TGT_LATLONG)
    log_TGT_LAT = float(log_TGT_LATLONG.split(",")[0])
    log_TGT_LON = float(log_TGT_LATLONG.split(",")[1])
    
    # convert ddmm.mmm to dd.ddd
    tgt_coord = coordinate_conversion(log_TGT_LAT, log_TGT_LON)
    log_TGT_LAT = tgt_coord['lat']
    log_TGT_LON = tgt_coord['lon']

    # GC control
    log_C_PITCH = ncdata.variables["log_C_PITCH"][:].tolist()
    log_PITCH_GAIN = ncdata.variables["log_PITCH_GAIN"][:].tolist()
    log_C_ROLL_DIVE = ncdata.variables["log_C_ROLL_DIVE"][:].tolist()
    log_C_ROLL_CLIMB = ncdata.variables["log_C_ROLL_CLIMB"][:].tolist()
    log_C_VBD = ncdata.variables["log_C_VBD"][:].tolist()
    log_MAX_BUOY = ncdata.variables["log_MAX_BUOY"][:].tolist()
    log_SM_CC = ncdata.variables["log_SM_CC"][:].tolist()
    
    # internal sensors
    log_HUMID = ncdata.variables["log_HUMID"][:].tolist()
    log_TEMP = ncdata.variables["log_TEMP"][:].tolist()
    
    try:
        raw_pressure = ncdata.variables["log_INTERNAL_PRESSURE"][:]
        try:
            # Try to decode if it is a character/byte array
            decoded_pressure = np.char.decode(raw_pressure, encoding='utf-8')
            log_INTERNAL_PRESSURE = float("".join(decoded_pressure))
        except TypeError:
            # If a TypeError occurs, it is already a numeric type
            log_INTERNAL_PRESSURE = float(np.atleast_1d(raw_pressure)[0])
    except Exception:
        # Catchall for missing variable, ValueError, or other extraction failures
        log_INTERNAL_PRESSURE = -9.999
        
    # surface transmission parameters
    log_SM_DEPTHo = ncdata.variables["log__SM_DEPTHo"][:].tolist()
    log_SM_ANGLEo = ncdata.variables["log__SM_ANGLEo"][:].tolist()
    log_CALLS = ncdata.variables["log__CALLS"][:].tolist()
    log_ERRORS = np.char.decode(ncdata.variables["log_ERRORS"], encoding='utf-8')
    log_ERRORS = "".join(log_ERRORS)


    # battery status     
    log_24V_AH_raw = np.char.decode(ncdata.variables["log_24V_AH"], encoding='utf-8') 
    log_24V_AH = "".join(log_24V_AH_raw).split(",")
    log_10V_AH_raw = np.char.decode(ncdata.variables["log_10V_AH"], encoding='utf-8') 
    log_10V_AH = "".join(log_10V_AH_raw).split(",")
    try:
        log_24_minv = float(log_24V_AH[0])
    except (IndexError, ValueError):
        log_24_minv = 0.0

    try:
        log_10_minv = float(log_10V_AH[0])
    except (IndexError, ValueError):
        log_10_minv = 0.0
       
    # compute total Ah in both batteries 
    # 26Ah x 11 cells = 286Ah for the "24V pack", and 26Ah x 3 cells = 78 Ah for the "10V pack". This totals 364 Ah, and we use 310 Ah (85%).
    log_AH0_24V = ncdata.variables["log_AH0_24V"][:].tolist() # total battery capacity Ah = 310 Ah
    log_AH0_10V = ncdata.variables["log_AH0_10V"][:].tolist() # total battery capacity Ah
    log_AH_total_capacity = log_AH0_24V + log_AH0_10V # total Ah usually assigned 310 Ah to one of the two in cmdfile: $AH0_24V,0 $AH0_10V,310    
    # compute Ah fuel gauge reading at the beggining of the dive
    log_FG_AHR_24Vo = float(np.atleast_1d(ncdata.variables["log_FG_AHR_24Vo"][:])[0])
    log_FG_AHR_10Vo = float(np.atleast_1d(ncdata.variables["log_FG_AHR_10Vo"][:])[0]) 
    log_FG_AHR_Vo = log_FG_AHR_10Vo + log_FG_AHR_24Vo # this is assigned as the total Ah used (basestation website scripts)
    # compute Ah fuel gauge reading at the end of the dive    
    log_FG_AHR_24V = float(np.atleast_1d(ncdata.variables["log_FG_AHR_24V"][:])[0])
    log_FG_AHR_10V = float(np.atleast_1d(ncdata.variables["log_FG_AHR_10V"][:])[0])   
    log_FG_AHR_V = log_FG_AHR_10V + log_FG_AHR_24V

    # Calculations as in basestation website scrips
    # In this database creation script, APL defines the fuel gauge Amp-hours used during a dive as Initial - Final (Vo - V) 
    # because the Seaglider's hardware fuel gauge registers decrement (count downwards) as energy is consumed.Because the fuel gauge 
    # tracks discharge by counting down, the value at the end of the dive is strictly mathematically lower than the value at the start of the dive. 
    # Subtracting the final value from the initial value is required to yield a positive number representing the capacity consumed.
    # Depending on the specific fuel gauge hardware revision inside the glider, this downward count happens in one of two ways:
    # The gauge is programmed with the battery's total capacity (e.g., $150Ah$) and counts down towards zero. (e.g., $Initial = 150$, $Final = 148$. $150 - 148 = +2Ah$ used).
    log_AH_thisdive = log_FG_AHR_Vo - log_FG_AHR_V # in Ah

    # get stats from arrays of currents, ad rates
    gc_values = get_gc_values(ncdata)

    # compile ncfile log data for table into dictionary only with desired parameters
    thisdive = {
    "dive" : int(np.atleast_1d(log_dive)[0]), 
    "time_start" : str(log_gps_time_utc[1]), 
    "time_end" : str(log_gps_time_utc[2]),
    "gps_lat_start" : float(log_gps_lat[1]),
    "gps_lon_start" : log_gps_lon[1],
    "gps_lat_end" : log_gps_lat[2],
    "gps_lon_end" : log_gps_lon[2],
    "D_TGT" : log_D_TGT,
    "D_ABORT" : log_D_ABORT,
    "T_DIVE" : log_T_DIVE,
    "T_MISSION" : log_T_MISSION,
    "T_ABORT" : log_T_ABORT,
    "C_PITCH" : log_C_PITCH,
    "PITCH_GAIN" : log_PITCH_GAIN,
    "C_ROLL_DIVE" : log_C_ROLL_DIVE,
    "C_ROLL_CLIMB" : log_C_ROLL_CLIMB,
    "C_VBD" : log_C_VBD,
    "MAX_BUOY" : log_MAX_BUOY,
    "NAV_MODE" : log_NAV_MODE,
    "HEADING" : log_HEADING,
    "TGT_name" : log_TGT_NAME,
    "TGT_lat" : log_TGT_LAT,
    "TGT_lon" : log_TGT_LON,
    "int_Humidity" : log_HUMID,
    "int_Pressure" : log_INTERNAL_PRESSURE,
    "int_Temperature" : log_TEMP,
    "SM_CC" : log_SM_CC,
    "SM_angle" : log_SM_ANGLEo,
    "SM_depth" : log_SM_DEPTHo,
    "CALLS" : log_CALLS,
    "ERRORS" : log_ERRORS,
    "dac_velocity" : dac_velocity,
    "dac_heading" : dac_heading,
    "surf_velocity" : surf_velocity,
    "surf_heading" : surf_heading,
    "glider_sog" : glider_sog,
    "glider_dog" : glider_dog,
    "glider_hdg" : glider_hdg,
    "glider_dive_time" : glider_dive_time,
    "roll_imax" : gc_values["roll_imax"],
    "pitch_imax" : gc_values["pitch_imax"],
    "vbd_imax" : gc_values["vbd_imax"],
    "roll_rate_min" : gc_values["roll_rate_min"],
    "pitch_rate_min" : gc_values["pitch_rate_min"],
    "vbd_rate_min" : gc_values["vbd_rate_min"],
    "vbd_i_apogee" : gc_values["vbd_i_apogee"],
    "vbd_rate_apogee" : gc_values["vbd_rate_apogee"],
    "depth_reached" : gc_values["depth_reached"],
    "log_AH_total_capacity" : log_AH_total_capacity,    
    "log_AH_total_consumed" : log_FG_AHR_Vo,
    "log_24_minv" : log_24_minv,
    "log_10_minv" : log_10_minv,
    "log_AH_thisdive" : log_AH_thisdive
    }

    # Extract all variables for JSON while the file is still in RAM
    all_nc_data = extract_all_variables(ncdata)
    ncdata.close()

    return thisdive, all_nc_data

# get currents and AD drates statistics from arrays of values
def get_gc_values(ncdata):
    vbd_ad_start = ncdata['gc_vbd_ad_start'][:].tolist()
    pitch_ad_start = ncdata['gc_pitch_ad_start'][:].tolist()
    roll_ad_start = ncdata['gc_roll_ad_start'][:].tolist()
    
    vbd_ad = ncdata['gc_vbd_ad'][:].tolist()
    pitch_ad = ncdata['gc_pitch_ad'][:].tolist()
    roll_ad = ncdata['gc_roll_ad'][:].tolist()
    
    vbd_secs = ncdata['gc_vbd_secs'][:].tolist()
    pitch_secs = ncdata['gc_pitch_secs'][:].tolist()
    roll_secs = ncdata['gc_roll_secs'][:].tolist()
    
    vbd_i = (ncdata['gc_vbd_i'][:] * 1000).tolist() # scale to milliamps
    pitch_i = (ncdata['gc_pitch_i'][:] * 1000).tolist() # scale to milliamps
    roll_i = (ncdata['gc_roll_i'][:] * 1000).tolist() # scale to milliamps
    
    depths = ncdata['gc_depth'][:].tolist()

    # calculate rates based on startand, AD values and time
    vbd_rates = get_rate(vbd_ad, vbd_ad_start, vbd_secs)
    pitch_rates = get_rate(pitch_ad, pitch_ad_start, pitch_secs) 
    roll_rates = get_rate(roll_ad, roll_ad_start, roll_secs)

    # dictionary with lists
    data = {'vbd_secs':vbd_secs, 'pitch_secs':pitch_secs, 'roll_secs':roll_secs,
        'vbd_i':vbd_i, 'pitch_i':pitch_i, 'roll_i':roll_i,
        'vbd_rates':vbd_rates, 'pitch_rates':pitch_rates, 'roll_rates':roll_rates,
        'depths':depths }

    # convert to dataframe for easier stats and filtering
    df_gc = pd.DataFrame(data)

    # get max currents filtered for gc-time > timefilter
    roll_imax = ((df_gc[df_gc["roll_secs"] > timefilter])["roll_i"]).max()
    pitch_imax = ((df_gc[df_gc["pitch_secs"] > timefilter])["pitch_i"]).max()
    vbd_imax = ((df_gc[df_gc["vbd_secs"] > timefilter])["vbd_i"]).max()
    
    # get mean currents
    roll_i_mean = ((df_gc[df_gc["roll_secs"] > timefilter])["roll_i"]).mean()
    pitch_i_mean = ((df_gc[df_gc["pitch_secs"] > timefilter])["pitch_i"]).mean()
    vbd_i_mean = ((df_gc[df_gc["vbd_secs"] > timefilter])["vbd_i"]).mean()    
    
    # get min rates
    roll_rate_min = (((df_gc[ (df_gc["roll_secs"] > timefilter) & (df_gc["roll_rates"].abs() > 0) ])["roll_rates"]).abs()).min()
    pitch_rate_min = (((df_gc[ (df_gc["roll_secs"] > timefilter) & (df_gc["pitch_rates"].abs() > 0) ])["pitch_rates"]).abs()).min()
    vbd_rate_min = (((df_gc[ (df_gc["roll_secs"] > timefilter) & (df_gc["vbd_rates"].abs() > 0)])["vbd_rates"]).abs()).min()
    
    # get mean rates
    roll_rate_mean = (((df_gc[df_gc["roll_secs"] > timefilter])["roll_rates"]).abs()).mean()
    pitch_rate_mean = (((df_gc[df_gc["roll_secs"] > timefilter])["pitch_rates"]).abs()).mean()
    vbd_rate_mean = (((df_gc[df_gc["roll_secs"] > timefilter])["vbd_rates"]).abs()).mean()    
    
    # get apogee values
    idx_max_depth = df_gc["depths"].idxmax()
    vbd_i_apogee = df_gc.loc[idx_max_depth, "vbd_i"]
    vbd_rate_apogee = df_gc.loc[idx_max_depth, "vbd_rates"]
    depth_reached = df_gc["depths"].max()

    gc_values = {"roll_imax": roll_imax, "pitch_imax": pitch_imax, "vbd_imax":vbd_imax,
                 "roll_i_mean": roll_i_mean, "pitch_i_mean": pitch_i_mean, "vbd_i_mean" : vbd_i_mean,
                 "roll_rate_min" : roll_rate_min, "pitch_rate_min" : pitch_rate_min, "vbd_rate_min" : vbd_rate_min,
                 "roll_rate_mean" : roll_rate_mean, "pitch_rate_mean" : pitch_rate_mean, "vbd_rate_mean" : vbd_rate_mean,
                 "vbd_i_apogee" : vbd_i_apogee, "vbd_rate_apogee" : vbd_rate_apogee, "depth_reached" : depth_reached}

    return gc_values

# calculate AD rates
def get_rate(ad_start, ad_end, time):
    rates = []
    # iterate over 3 lists simultaneously
    for st, end, t in zip(ad_start, ad_end, time):
        if t <= timefilter:
            rate = 0.0
        else:
            rate = (end - st)/t
        rates.append(rate)
    return rates

# convert 'targets' file ddmm.mmm coordinates to dd.ddd
def coordinate_conversion(lat,lon):
    lat = int(lat/100.0) + (lat % 100)/60.0 
      
    if lon < 0:        
        lon = int(lon/100.0) - (abs(lon) % 100)/60.0
    else:
        lon = int(lon/100.0) + (abs(lon) % 100)/60.0
    
    dec_coord = {'lat':lat, 'lon':lon}
    return dec_coord



# read all the variables and values to export a json file
# Reads a NetCDF file and extracts all variables and their values into a dictionary
def get_all_variables(ncfile):    
    
    nc_obj = nc.Dataset(ncfile)
    all_data = {}
    
    for var in nc_obj.variables:
        raw_val = nc_obj.variables[var][:]
        
        # Try decoding byte/char arrays into readable strings
        if raw_val.dtype.kind in ['S', 'U']:
            try:
                decoded = np.char.decode(raw_val, encoding='utf-8')
                # Join arrays of chars into a single string and strip whitespace
                all_data[var] = "".join(np.atleast_1d(decoded)).strip()
            except Exception:
                all_data[var] = raw_val.tolist()
        else:
            # Handle masked arrays by filling missing values (e.g. -9.999)
            if np.ma.isMaskedArray(raw_val):
                raw_val = raw_val.filled(-9.999)
            
            # Convert NumPy arrays to standard Python lists
            val_list = np.atleast_1d(raw_val).tolist()
            
            # Unbox single values for cleaner JSON
            if len(val_list) == 1:
                all_data[var] = val_list[0]
            else:
                all_data[var] = val_list
                
    nc_obj.close()
    return all_data