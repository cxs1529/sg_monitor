import pandas as pd
from .ncdata import haversine
from .thresholds import *


# classification lists per dashboard container: navigation, call, health, rates-currents
navigation_keys = ["dive", "time_end", "gps_lat_end", "gps_lon_end", "TGT_name", "TGT_lat",  
                    "tgt_distance", "tgt_time", "TGT_lon", "glider_sog", "glider_dog", "glider_hdg",
                    "glider_dive_time", "depth_reached"]

call_keys = ["SM_angle", "SM_depth", "CALLS"]

health_keys= ["int_Humidity", "int_Pressure", "int_Temperature", "minVoltage", "batteryPercent", "errors"]

current_rates_keys = ["roll_imax", "pitch_imax", "vbd_imax", "roll_rate_min", "pitch_rate_min", "vbd_rate_min",
                       "vbd_i_apogee", "vbd_rate_apogee"]

# returns a dictionary with values from last dive only
def glider_stats(df):
    # pd.set_option('display.max_columns', None)
    # print(df)

    # retrieve values from last dive
    dive = df.loc[0,"dive"]
    # position
    depth_reached = df.loc[0,"depth_reached"]
    dtarget = df.loc[0,"D_TGT"]

    time_end = df.loc[0,"time_end"]
    gps_lat_end = df.loc[0,"gps_lat_end"]
    gps_lon_end = df.loc[0,"gps_lon_end"]

    TGT_name = df.loc[0,"TGT_name"]
    TGT_lat = df.loc[0,"TGT_lat"]
    TGT_lon = df.loc[0,"TGT_lon"]
    # internal sensors
    int_Humidity = df.loc[0,"int_Humidity"]
    int_Pressure = df.loc[0,"int_Pressure"]
    int_Temperature = df.loc[0,"int_Temperature"]
    
    # tx position
    SM_angle = df.loc[0,"SM_angle"]
    SM_depth = df.loc[0,"SM_depth"]
    calls = df.loc[0,"CALLS"]
    # displacement
    glider_sog = df.loc[0,"glider_sog"] # m/s
    glider_hdg = df.loc[0,"glider_hdg"] # deg
    glider_dog = df.loc[0,"glider_dog"] # km
    glider_dive_time = df.loc[0,"glider_dive_time"] # seconds
    tdive = df.loc[0,"T_DIVE"] # minutes
    # GC currents and rates
    roll_imax = df.loc[0,"roll_imax"]
    pitch_imax = df.loc[0,"pitch_imax"]
    vbd_imax = df.loc[0,"vbd_imax"]

    roll_rate_min = df.loc[0,"roll_rate_min"]
    pitch_rate_min = df.loc[0,"pitch_rate_min"]
    vbd_rate_min = df.loc[0,"vbd_rate_min"]

    vbd_i_apogee = df.loc[0,"vbd_i_apogee"]
    vbd_rate_apogee = df.loc[0,"vbd_rate_apogee"]

    # battery state
    log_24_minv = df.loc[0,"log_24_minv"]
    log_10_minv = df.loc[0,"log_10_minv"]
    # minVoltage = min(log_24_minv, log_10_minv)
    log_AH_total_capacity = df.loc[0,"log_AH_total_capacity"]
    log_AH_total_consumed = df.loc[0,"log_AH_total_consumed"]
    batteryPercent = (log_AH_total_capacity - log_AH_total_consumed)/log_AH_total_capacity

    log_energy_thisdive = df.loc[0,"log_energy_thisdive"]
    battery_ndives = (log_AH_total_capacity - log_AH_total_consumed)/log_energy_thisdive # number of dives to do at current energy consumption (based on last dive)
    # Add something for error array
    errors = (df.loc[0,"ERRORS"]).split(",")
    
    error_dict = {"pitch_error": errors[0], "roll_error": errors[1], "vbd_error": errors[2], "pitch_retry": errors[3], "roll_retry": errors[4],
                    "vbd_retry": errors[5], "gps_timeout": errors[6], "compass_timeout": errors[7], 
                    "sensor_timeout": str(errors[8]) + "-" + str(errors[9]) + "-" + str(errors[10]) + "-" + str(errors[11]) }

    # time and distance to target
    tgt_displacement = haversine(gps_lat_end,gps_lon_end, TGT_lat, TGT_lon) # km
    tgt_distance = tgt_displacement["distance"]
    tgt_direction = tgt_displacement["heading"] # could be used to determine if glider is moving away or towards target
    tgt_time = (tgt_distance * 1000 /glider_sog )/3600 # hs


    
    dashboard_dict = {
    "dive" : dive,     
    "time_end" : time_end,
    "gps_lat_end" : gps_lat_end,
    "gps_lon_end" : gps_lon_end,
    "TGT_name" : TGT_name,
    "TGT_lat" : TGT_lat,
    "TGT_lon" : TGT_lon,
    "int_Humidity" : int_Humidity,
    "int_Pressure" : int_Pressure,
    "int_Temperature" : int_Temperature,
    "SM_angle" : SM_angle,
    "SM_depth" : SM_depth,
    "CALLS" : calls,
    "glider_sog" : glider_sog,
    "glider_dog" : glider_dog,
    "glider_hdg" : glider_hdg,
    "glider_dive_time" : glider_dive_time,
    "T_DIVE" : tdive,
    "roll_imax" : roll_imax,
    "pitch_imax" : pitch_imax,
    "vbd_imax" : vbd_imax,
    "roll_rate_min" : roll_rate_min,
    "pitch_rate_min" : pitch_rate_min,
    "vbd_rate_min" : vbd_rate_min,
    "vbd_i_apogee" : vbd_i_apogee,
    "vbd_rate_apogee" : vbd_rate_apogee,
    "depth_reached" : depth_reached,
    "D_TGT" : dtarget,
    "log_24_minv" : log_24_minv,
    "log_10_minv" : log_10_minv,    
    "batteryPercent" : batteryPercent,
    "battery_ndives" : battery_ndives,
    "tgt_distance" : tgt_distance,
    "tgt_time" : tgt_time,
    "tgt_direction": tgt_direction,
    "errors" : error_dict
    # "errors" : errors
    }

    return dashboard_dict


# create html for health parameters dashboard
def get_health_html(dash_data):
    batsf = 0.9 # safety factor for battery remaining dives estimate

    t = "internal humidity"
    # Fixed: Used single quotes for 'int_Humidity'
    humiditystr = f"<div class='health-div'>\n <h3 title='{t}'>HUMIDITY</h3>\n <p class={get_class(dash_data, 'int_Humidity')}>{dash_data['int_Humidity']} %</p>\n   </div>\n"

    t = "internal temperature"
    # Fixed: Used single quotes for 'int_Temperature'
    temperaturestr = f"<div class='health-div'>\n <h3 title='{t}'>TEMPERATURE</h3>\n <p class={get_class(dash_data, 'int_Temperature')}>{dash_data['int_Temperature']} {chr(176)}C</p>\n </div>\n"

    t = "internal pressure ~ 14.7-5 psi"
    # Fixed: Simplified formatting (removed nested f-string) and used single quotes
    pressurestr = f"<div class='health-div'>\n <h3 title='{t}'>PRESSURE</h3>\n <p class={get_class(dash_data, 'int_Pressure')}>{dash_data['int_Pressure']:.2f} psi</p>\n </div>\n"

    # usually _24_ tracks the actual voltage
    t = "Firmware only tracks one variable: 10V or 24V"
    # Fixed: Used single quotes for keys
    voltminstr = f"<div class='health-div'>\n <h3 title='{t}'>VOLTAGE</h3>\n <p class={get_class(dash_data, 'log_24_minv')}>\"24V\": {dash_data['log_24_minv']} V | \"15V\": {dash_data['log_10_minv']} V</p>\n </div>\n"

    # 10% safety factor
    t = "Based on 310 Ah battery (estimate with 10% safety factor)"
    # Fixed: Simplified formatting and math
    days_calc = (dash_data['battery_ndives'] * batsf * dash_data['glider_dive_time'] / 3600) / 24.0
    batterystr = f"<div class='health-div'>\n <h3 title='{t}'>BATTERY</h3>\n <p class={get_class(dash_data, 'batteryPercent')}>{dash_data['batteryPercent']*100:.1f} % \
       ({int(dash_data['battery_ndives'] * batsf)} dives | {days_calc:.2f} days )</p>\n </div>\n"

    html_string = "<div class=\"health-container\">\n" + humiditystr + pressurestr + temperaturestr + voltminstr + batterystr + "</div>\n"

    return html_string


def get_error_html(dash_data):
    # Fixed: Switched all inner quotes to single quotes
    pitchstr = f"<div class='error-div'>\n <h3 title='something pitch' >PITCH</h3>\n <p class={get_class(dash_data['errors'], 'pitch_error')}>\
        {dash_data['errors']['pitch_error']} | {dash_data['errors']['pitch_retry']}</p>\n </div>\n"
    
    rollstr = f"<div class='error-div'>\n <h3>ROLL</h3>\n <p class={get_class(dash_data['errors'], 'roll_error')}>\
        {dash_data['errors']['roll_error']} | {dash_data['errors']['roll_retry']}</p>\n </div>\n"
    
    vbdstr = f"<div class='error-div'>\n <h3>VBD</h3>\n <p class={get_class(dash_data['errors'], 'vbd_error')}>\
        {dash_data['errors']['vbd_error']} | {dash_data['errors']['vbd_retry']}</p>\n </div>\n"

    gpsstr = f"<div class='error-div'>\n <h3>GPS TIMEOUT</h3>\n <p class={get_class(dash_data['errors'], 'gps_timeout')}>{dash_data['errors']['gps_timeout']}</p>\n </div>\n"
    
    compassstr = f"<div class='error-div'>\n <h3>COMPASS TIMEOUT</h3>\n <p class={get_class(dash_data['errors'], 'compass_timeout')}>{dash_data['errors']['compass_timeout']}</p>\n </div>\n"
    
    sensorstr = f"<div class='error-div'>\n <h3>SENSOR TIMEOUT</h3>\n <p class={get_class(dash_data['errors'], 'sensor_timeout')}>{dash_data['errors']['sensor_timeout']}</p>\n </div>\n"

    html_string = "<div class=\"error-container\">\n" + pitchstr + rollstr + vbdstr + gpsstr + compassstr + sensorstr + "</div>\n"

    return html_string


# create html for call parameters dashboard
def get_call_html(dash_data):
    # Fixed: Switched all inner quotes to single quotes
    callanglestr = f"<div class='call-div'>\n <h3>CALL ANGLE</h3>\n <p class={get_class(dash_data, 'SM_angle')}>{dash_data['SM_angle']}</p>\n </div>\n"
    calldepthestr = f"<div class='call-div'>\n <h3>CALL DETPH</h3>\n <p class={get_class(dash_data, 'SM_depth')}>{dash_data['SM_depth']}</p>\n </div>\n"
    callnumstr = f"<div class='call-div'>\n <h3>CALLS</h3>\n <p class={get_class(dash_data, 'CALLS')}>{int(dash_data['CALLS'])}</p>\n </div>\n"

    html_string = "<div class=\"call-container\">\n" + callanglestr +  calldepthestr + callnumstr + "</div>\n"
    return html_string


# create html for navigation parameters dashboard
def get_navigation_html(dash_data):
    # Fixed: Switched all inner quotes to single quotes and simplified f-string formatting
    divestr = f"<div class='nav-div'>\n <h3>DIVE</h3>\n <p class='p-normal'>{dash_data['dive']}</p>\n </div>\n"

    depthstr = f"<div class='nav-div'>\n <h3>MAX DEPTH</h3>\n <p class={get_class(dash_data, 'depth_reached')}>{round(dash_data['depth_reached'],0)} m <br><br> \
                 * D_TGT: {int(dash_data['D_TGT'])} *</p>\n </div>\n"    

    timestr = f"<div class='nav-div'>\n <h3>DATE TIME</h3>\n <p class='p-normal'>{ztime(dash_data['time_end'])}</p>\n </div>\n"

    positionstr = f"<div class='nav-div'>\n <h3>POSITION</h3>\n <p class='p-normal'>{dash_data['gps_lat_end']:.4f}, \
                    {dash_data['gps_lon_end']:.4f}</p>\n </div>\n" 
       
    targetstr = f"<div class='nav-div'>\n <h3>TARGET</h3>\n <p class='p-normal'> <p style=\"font-weight: bold; font-style: italic;\">{dash_data['TGT_name']}</p>{dash_data['TGT_lat']:.4f}, \
                    {dash_data['TGT_lon']:.4f} <br> DTT: {dash_data['tgt_distance']:.2f} km \
                    <br>TTG: {dash_data['tgt_time']:.1f} h ({dash_data['tgt_time']/24:.1f} d)</p>\n </div>\n"
    
    sogstr = f"<div class='nav-div'>\n <h3>SOG</h3>\n <p class='p-normal'>{dash_data['glider_sog']:.2f} m/s \
                    ({dash_data['glider_sog'] * 3600 / 1000:.2f} km/h) </p>\n </div>\n"

    dogstr = f"<div class='nav-div'>\n <h3>DOG</h3>\n <p class={get_class(dash_data, 'glider_dog')}>{dash_data['glider_dog']:.2f} km | \
                    {dash_data['glider_hdg']:.0f} {chr(176)} </p>\n <br> \
                    Off to target by: {dash_data['tgt_direction'] - dash_data['glider_hdg']:.0f} {chr(176)}</div>\n"

    divetime = f"<div class='nav-div'>\n <h3>DIVE TIME</h3>\n <p class={get_class(dash_data, 'glider_dive_time')}> \
        {dash_data['glider_dive_time']/60.0:.0f} min ({dash_data['glider_dive_time']/3600.0:.1f} h) <br><br> \
                    * T_DIVE: {int(dash_data['T_DIVE'])} *</p>\n </div>\n"

    html_string = "<div class=\"nav-container\">\n" + divestr + depthstr + timestr + positionstr + targetstr + sogstr + dogstr + divetime + "</div>\n"
    
    return html_string


def get_rates_html(dash_data):
    # Fixed: Switched all inner quotes to single quotes
    # vbd
    vbdimaxstr = f"<div class='rates-div'>\n <h3>VBD I MAX</h3>\n <p class={get_class(dash_data, 'vbd_imax')}>{int(dash_data['vbd_imax'])} mA</p>\n </div>\n"
    vbdiapstr = f"<div class='rates-div'>\n <h3>VBD I APOGEE</h3>\n <p class={get_class(dash_data, 'vbd_i_apogee')}>{int(dash_data['vbd_i_apogee'])} mA</p>\n </div>\n"
    vbdrateminstr = f"<div class='rates-div'>\n <h3>VBD RATE MIN</h3>\n <p class={get_class(dash_data, 'vbd_rate_min')}>{dash_data['vbd_rate_min']:.2f} AD/s</p>\n </div>\n"
    vbdrateapstr = f"<div class='rates-div'>\n <h3>VBD RATE APOGEE</h3>\n <p class={get_class(dash_data, 'vbd_rate_apogee')}>{dash_data['vbd_rate_apogee']:.2f} AD/s</p>\n </div>\n"
    # roll
    rollimaxstr = f"<div class='rates-div'>\n <h3>ROLL I MAX</h3>\n <p class={get_class(dash_data, 'roll_imax')}>{int(dash_data['roll_imax'])} mA</p>\n </div>\n"
    rollrateminstr = f"<div class='rates-div'>\n <h3>ROLL RATE MIN</h3>\n <p class={get_class(dash_data, 'roll_rate_min')}>{int(dash_data['roll_rate_min'])} AD/s</p>\n </div>\n"
    # pitch
    pitchimaxstr = f"<div class='rates-div'>\n <h3>PITCH I MAX</h3>\n <p class={get_class(dash_data, 'pitch_imax')}>{int(dash_data['pitch_imax'])} mA</p>\n </div>\n"
    pitchrateminstr = f"<div class='rates-div'>\n <h3>PITCH RATE MIN</h3>\n <p class={get_class(dash_data, 'pitch_rate_min')}>{int(dash_data['pitch_rate_min'])} AD/s</p>\n </div>\n"

    html_string = "<div class=\"rates-container\">\n" + vbdimaxstr + vbdiapstr + vbdrateminstr + vbdrateapstr + rollimaxstr + rollrateminstr + pitchimaxstr + pitchrateminstr + "</div>\n"

    return html_string


def ztime(timestr):
    dt = timestr.split("T")
    dthtml = dt[0] + "<br>" + dt[1].replace("Z", "") + " UTC"

    return dthtml

# Returns the tooltip html sentence with specific parameter text
def tip(text):
    str = f"<span class=\"tooltip-text\">{text}</span>"
    return str


# return paragraph item class based on thresholds
def get_class(dict,key):
    key_class = "p-normal"

    # Navigation
    if key == "glider_dog":
        if dict[key] <= dog_thd["min"] or dict[key] >= dog_thd["max"]:
            key_class = "p-warning"
    elif key == "glider_sog":
        if dict[key] <= sog_thd["min"] or dict[key] >= sog_thd["max"]:
            key_class = "p-warning"
    elif key == "glider_dive_time":
        if (dict[key]/60) <= dict["T_DIVE"] * 0.85 or (dict[key]/60) >= dict["T_DIVE"] * 1.15:
            key_class = "p-warning" 
    elif key == "depth_reached":
        if dict[key] <= dict["D_TGT"] * 0.95 or dict[key] >= dict["D_TGT"] * 1.05:
            key_class = "p-warning" 
    # Health
    elif key == "int_Humidity":
        if dict[key] <= int_Humidity_thd["min"] or dict[key] >= int_Humidity_thd["max"]:
            key_class = "p-warning"
    elif key == "int_Temperature":
        if dict[key] <= int_Temperature_thd["min"] or dict[key] >= int_Temperature_thd["max"]:
            key_class = "p-warning"  
    elif key == "int_Pressure":
        if dict[key] <= int_Pressure_thd["min"] or dict[key] >= int_Pressure_thd["max"]:
            key_class = "p-warning" 
    elif key == "log_24_minv":
        if dict[key] <= battery_volt_thd["min"] or dict[key] >= battery_volt_thd["max"]:
            key_class = "p-warning"  
    elif key == "batteryPercent":
        if dict[key] <= battery_percent_thd["min"] or dict[key] >= battery_percent_thd["max"]:
            key_class = "p-warning"  
    # Errors
    elif key == "pitch_error" or key == "roll_error" or key == "vbd_error":
        if int(dict[key]) >= error_thd["max"]:
            key_class = "p-warning"   
    # Calls
    elif key == "SM_angle":
        if abs(dict[key]) <= SM_angle_thd["min"] or dict[key] >= SM_angle_thd["max"]:
            key_class = "p-warning"   
    elif key == "SM_depth":
        if dict[key] <= SM_depth_thd["min"] or dict[key] >= SM_depth_thd["max"]:
            key_class = "p-warning" 
    elif key == "CALLS":
        if dict[key] <= CALLS_thd["min"] or dict[key] >= CALLS_thd["max"]:
            key_class = "p-warning"   
    # Rates        
    elif key == "vbd_imax" or key == "vbd_i_apogee":
        if dict[key] <= vbd_imax_thd["min"] or dict[key] >= vbd_imax_thd["max"]:
            key_class = "p-warning"
    elif key == "vbd_rate_min" or key == "vbd_rate_apogee":
        if dict[key] <= vbd_rate_thd["min"] or dict[key] >= vbd_rate_thd["max"]:
            key_class = "p-warning"  
    elif key == "roll_imax":
        if dict[key] <= roll_imax_thd["min"] or dict[key] >= roll_imax_thd["max"]:
            key_class = "p-warning"  
    elif key == "roll_rate_min":
        if dict[key] <= roll_rate_thd["min"] or dict[key] >= roll_rate_thd["max"]:
            key_class = "p-warning" 
    elif key == "pitch_imax":
        if dict[key] <= pitch_imax_thd["min"] or dict[key] >= pitch_imax_thd["max"]:
            key_class = "p-warning"
    elif key == "pitch_rate_min":
        if dict[key] <= roll_rate_thd["min"] or dict[key] >= roll_rate_thd["max"]:
            key_class = "p-warning"                    
    else:
        pass

    return key_class 
          
        


# def get_card_string(key, dict):

#     if key in navigation_keys:
#         card_class = "nav-div"
#     elif key in call_keys:
#         card_class = "call-div"    
#     elif key in health_keys:
#         card_class = "health-div"
#     elif key in current_rates_keys:
#         card_class = "currents-div"
#     else:
#         pass
    
    
#     if key == "dive":
#           card_title = "DIVE"
#           card_value_class = "p-normal"
#           card_value = str(int(dict[key]))
#     elif key == "time_end":
#           card_title = "TIME"
#           card_value_class = "p-normal"
#           card_value = dict[key]
#     elif key == "gps_lat_end":
#           card_title = "LAT"
#           card_value_class = "p-normal"
#           card_value = str(f"{round(dict[key], 4):.4f}")  
#     elif key == "gps_lon_end":
#           card_title = "LON"
#           card_value_class = "p-normal"
#           card_value = str(f"{round(dict[key], 4):.4f}")
#     elif key == "TGT_name":
#           card_title = "TARGET"
#           card_value_class = "p-normal"
#           card_value = dict[key]

#     htmlstr = f"<div class={card_class}>\n <h3>{card_title}</h3>\n <p class={card_value_class} >{card_value}</p>\n  </div>\n"

#     return htmlstr