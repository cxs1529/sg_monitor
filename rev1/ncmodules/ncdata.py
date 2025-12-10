import netCDF4 as nc 
import numpy as np
import pandas as pd
from datetime import datetime, UTC

# User input
timefilter = 1 # [sec] filter out values with an action time of less than timefiler

# MAIN ------------------------------------------------------------------------------------------------------
# def main():
    
#     thisdive_dict = process_netcdf(ncfile)
#     print_dictionary(thisdive_dict)

#     df = pd.DataFrame(thisdive_dict, index=[0])
    










# MAIN ------------------------------------------------------------------------------------------------------






# FUNCTIONS

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
        print("> t:",t)    
        # dt = datetime.fromtimestamp(t, UTC)
        dt = datetime.fromtimestamp(t)
        print("> dt:",dt)
        dt_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("> dt_str:", dt_str)
        log_gps_time_utc.append(dt_str)
        
    # derived dive time
    glider_dive_time = log_gps_time[-1] - log_gps_time[-2] # time between last 2 gps fixes. Take into account time for maneuvers
    total_flight_time_s = ncdata.variables["total_flight_time_s"][:].tolist()
    # log_gps_lat and log_gps_lon are lists with [GPS1 GPS2 GPS] >> 1st-fix 2nd-fix --dive-- fix-post-dive > determine DOG with GPS2 and GPS
    displacement = haversine(float(log_gps_lat[1]), float(log_gps_lon[1]), float(log_gps_lat[2]), float(log_gps_lon[2])) # distance over ground [km] and bearing [deg]
    glider_dog = displacement["distance"]
    glider_hdg = displacement["heading"]
    glider_sog = glider_dog * 1000 /glider_dive_time # speed over ground [m/s]
    # sea currents
    depth_avg_curr_east = ncdata.variables["depth_avg_curr_east"][:].tolist() # in m/s
    depth_avg_curr_north = ncdata.variables["depth_avg_curr_north"][:].tolist()
    dac_velocity = np.hypot(depth_avg_curr_north,depth_avg_curr_east)
    dac_heading = (np.pi/2 - np.arctan2(depth_avg_curr_north, depth_avg_curr_east)) * 180.0 / np.pi

    surface_curr_east = ncdata.variables["surface_curr_east"][:].tolist() # in cm/s
    surface_curr_north = ncdata.variables["surface_curr_north"][:].tolist()
    surf_velocity = np.hypot(surface_curr_north, surface_curr_east) / 100.0 # in m/s
    surf_heading = (np.pi/2 - np.arctan2(surface_curr_north, surface_curr_east)) * 180.0 / np.pi
    # print(dac_velocity, "m/s",dac_heading, "deg || ", surf_velocity, "m/s", surf_heading, "deg")

    # control parameters
    # depth control
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
    log_INTERNAL_PRESSURE = np.char.decode(ncdata.variables["log_INTERNAL_PRESSURE"], encoding='utf-8') # convert numpy array of bytes to string
    log_INTERNAL_PRESSURE = float("".join(log_INTERNAL_PRESSURE))
    # surface transmission parameters
    log_SM_DEPTHo = ncdata.variables["log__SM_DEPTHo"][:].tolist()
    log_SM_ANGLEo = ncdata.variables["log__SM_ANGLEo"][:].tolist()
    log_CALLS = ncdata.variables["log__CALLS"][:].tolist()
    log_ERRORS = np.char.decode(ncdata.variables["log_ERRORS"], encoding='utf-8')
    log_ERRORS = "".join(log_ERRORS)
    #log_ERRORS = log_ERRORS.split(",")
    # battery status
    log_AH0_24V = ncdata.variables["log_AH0_24V"][:].tolist() # total battery capacity Ah
    log_AH0_10V = ncdata.variables["log_AH0_10V"][:].tolist() # total battery capacity Ah
    log_24V_AH = np.char.decode(ncdata.variables["log_24V_AH"], encoding='utf-8') # 2 values: Vmin during active phase, total battery Ah consumed since fuel gauge reset
    log_24V_AH = "".join(log_24V_AH) # result : 14.81,42.283
    log_24V_AH = log_24V_AH.split(",")
    log_10V_AH = np.char.decode(ncdata.variables["log_10V_AH"], encoding='utf-8') # 2 values: Vmin during active phase, total battery Ah consumed since fuel gauge reset
    log_10V_AH = "".join(log_10V_AH)
    log_10V_AH = log_10V_AH.split(",")

    log_24_minv = float(log_24V_AH[0])
    log_10_minv = float(log_10V_AH[0])
    log_24_ah_consumed = float(log_24V_AH[1])
    log_10_ah_consumed = float(log_10V_AH[1])
    # compute total energy
    log_AH_total_capacity = log_AH0_24V + log_AH0_10V
    log_AH_total_consumed = log_24_ah_consumed + log_10_ah_consumed
    
    # compute energy consumed in this dive
    log_FG_AHR_10Vo = ncdata.variables["log_FG_AHR_10Vo"][:].tolist() # end dive total energy consumed
    log_FG_AHR_24Vo = ncdata.variables["log_FG_AHR_24Vo"][:].tolist() # end dive
    log_FG_AHR_24V = ncdata.variables["log_FG_AHR_24V"][:].tolist() # before of dive
    log_FG_AHR_10V = ncdata.variables["log_FG_AHR_10V"][:].tolist() # before of dive
    
    log_battery_AH_diveEnd = log_FG_AHR_10Vo + log_FG_AHR_24Vo
    log_battery_AH_diveStart = log_FG_AHR_24V + log_FG_AHR_10V

    log_energy_thisdive = log_battery_AH_diveEnd - log_battery_AH_diveStart # this is only for the dive without what consumes at the surface

    # get stats from arrays of currents, ad rates
    gc_values = get_gc_values(ncdata)

    # compile ncfile log data for table into dictionary
    thisdive = {
    "dive" : int(log_dive), 
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
    "log_AH_total_consumed" : log_AH_total_consumed,
    "log_24_minv" : log_24_minv,
    "log_10_minv" : log_10_minv,
    "log_energy_thisdive" : log_energy_thisdive
    }
    #print(thisdive)

    return thisdive


# get currents and AD drates statistics from arrays of values
def get_gc_values(ncdata):
    # gc_vbd_ad_start gc_pitch_ad_start gc_roll_ad_start  
    vbd_ad_start = ncdata['gc_vbd_ad_start'][:].tolist()
    pitch_ad_start = ncdata['gc_pitch_ad_start'][:].tolist()
    roll_ad_start = ncdata['gc_roll_ad_start'][:].tolist()
    # gc_vbd_ad gc_pitch_ad gc_roll_ad
    vbd_ad = ncdata['gc_vbd_ad'][:].tolist()
    pitch_ad = ncdata['gc_pitch_ad'][:].tolist()
    roll_ad = ncdata['gc_roll_ad'][:].tolist()
    # gc_vbd_secs gc_pitch_secs gc_roll_secs 
    vbd_secs = ncdata['gc_vbd_secs'][:].tolist()
    pitch_secs = ncdata['gc_pitch_secs'][:].tolist()
    roll_secs = ncdata['gc_roll_secs'][:].tolist()
    # gc_vbd_i gc_pitch_i gc_roll_i
    vbd_i = (ncdata['gc_vbd_i'][:] * 1000).tolist() # scale to milliamps
    pitch_i = (ncdata['gc_pitch_i'][:] * 1000).tolist() # scale to milliamps
    roll_i = (ncdata['gc_roll_i'][:] * 1000).tolist() # scale to milliamps
    # gc_vbd_volts gc_pitch_volts gc_roll_volts
    #vbd_volts = ncdata['gc_vbd_volts'][:].tolist()
    #pitch_volts = ncdata['gc_pitch_volts'][:].tolist()
    #roll_volts = ncdata['gc_roll_volts'][:].tolist()
    # gc_depth
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