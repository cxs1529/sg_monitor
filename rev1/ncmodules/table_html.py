import pandas as pd
from .thresholds import *

# # define warning threshold values for conditional formatting
# int_Humidity_thd = {"min":40.0, "max": 70.0}
# int_Pressure_thd = {"min":9.2, "max": 10.0}
# int_Temperature_thd = {"min":15, "max": 35}
# SM_angle_thd = {"min":-75, "max": -50}
# SM_depth_thd = {"min":0.5, "max": 1.5}
# CALLS_thd = {"min":0, "max": 5}
# dac_velocity_thd = {"min":0, "max": 1}
# surf_velocity_thd = {"min":0, "max": 71} 
# vbd_rate_apogee_thd = {"min": 3.9, "max": 4.7} 
# vbd_imax_thd = {"min": 1000, "max": 2500} 


# returns a formated html table based on a dataframe
def convert_to_table(df):
    # headers to display in table
    filter_headers = ['dive', 'time_start', 'time_end', 'gps_lat_start', 'gps_lon_start',
       'gps_lat_end', 'gps_lon_end', 'D_TGT', 'D_ABORT', 'T_DIVE', 'T_MISSION',
       'T_ABORT', 'C_PITCH', 'PITCH_GAIN', 'C_ROLL_DIVE', 'C_ROLL_CLIMB',
       'C_VBD', 'MAX_BUOY', 'NAV_MODE', 'HEADING', 'TGT_name', 'TGT_lat',
       'TGT_lon', 'int_Humidity', 'int_Pressure', 'int_Temperature', 'SM_CC',
       'SM_angle', 'SM_depth', 'CALLS', 'ERRORS', 'dac_velocity',
       'dac_heading', 'surf_velocity', 'surf_heading', 'glider_sog',
       'glider_dog', 'glider_hdg', 'glider_dive_time', 
       'roll_imax', 'pitch_imax', 'vbd_imax', 'roll_rate_min', 'pitch_rate_min',
       'vbd_rate_min', 'vbd_i_apogee', 'vbd_rate_apogee', 'depth_reached', 
        "log_AH_total_capacity", "log_AH_total_consumed", "log_24_minv", "log_10_minv", "log_energy_thisdive" ] # 'filePath' removed
    
    #print(df.keys())  # prints all dataframe keys or headers

    # build header html string
    #print(">html for header:")  
    html_table_headers = "<tr class=\"table_header\">\n"
    for j in df.keys():
        if j in filter_headers:
            units = get_header_units(j)
            html_table_headers = html_table_headers + f"\n\t<th class=\"table_header\"> {j} {units} </th>" 

    html_table_headers = html_table_headers + "\n</tr>\n"
    #print(html_table_headers)

    # create html table string assuming diveN is in descending order
    #print(">html for data:")  
    html_table_data = ""    
    for i in range(0, len(df)):
        # start table row
        html_table_data = html_table_data + "\t\n<tr class=\"table_row\">\n"
        # iterate over data fields
        for col in filter_headers:            
            data_value, data_class = get_data_class(i, col, df)
            # build each table data entry
            html_table_data = html_table_data + f"\t<td class={data_class}> {data_value} </td>\n"
        # end table row
        html_table_data = html_table_data + "</tr>\n"
    #print(html_table_data)

    return html_table_headers + html_table_data


# returns the value and style class for a given dataframe item
def get_data_class(i, col, df):
    # default values to return
    data_class = "data_normal"
    data_value = df.loc[i,col]

    # parameter group classification for styling
    ctrl_parameters_int = ['D_TGT', 'D_ABORT', 'T_DIVE', 'T_MISSION',
       'T_ABORT', 'C_PITCH', 'C_ROLL_DIVE', 'C_ROLL_CLIMB',
       'C_VBD', 'MAX_BUOY', 'NAV_MODE', 'HEADING', 'SM_CC']
    ctrl_parameters_float = ['PITCH_GAIN']
    ctrl_parameters_str = ['TGT_name']
    gps_locations = ['gps_lat_start', 'gps_lon_start', 'gps_lat_end', 'gps_lon_end']
    velocities = ['dac_velocity',  'surf_velocity', 'glider_dog' ]
    headings = ['dac_heading', 'surf_heading', 'glider_hdg']
    ecurrents = ["roll_imax", "pitch_imax", "vbd_imax"]
    adrates = ["roll_rate_min", "pitch_rate_min", "vbd_rate_min"]

    # set style class based on parameter value exceeding normal values
    if col == "int_Humidity":
        data_value = round(data_value, 1)
        if data_value <= int_Humidity_thd["min"] or data_value >= int_Humidity_thd["max"]:
            data_class = "data_warning"
    elif col == "dive":
        data_value = int(data_value)
    elif col == "int_Pressure":
        data_value = round(data_value, 1)
        if data_value <= int_Pressure_thd["min"] or data_value >= int_Pressure_thd["max"]:
            data_class = "data_warning"
    elif col == "int_Temperature":
        data_value = round(data_value, 2)
        if data_value <= int_Temperature_thd["min"] or data_value >= int_Temperature_thd["max"]:
            data_class = "data_warning"        
    elif col == "SM_angle":
        data_value = int(round(data_value, 0))
        if abs(data_value) <= SM_angle_thd["min"] or abs(data_value) >= SM_angle_thd["max"]:
            data_class = "data_warning"        
    elif col == "SM_depth":
        data_value = round(data_value, 1)
        if data_value <= SM_depth_thd["min"] or data_value >= SM_depth_thd["max"]:
            data_class = "data_warning"         
    elif col == "CALLS":
        data_value = int(data_value)
        if data_value <= CALLS_thd["min"] or data_value >= CALLS_thd["max"]:
            data_class = "data_warning"        
    elif col == "dac_velocity":
        data_value = round(data_value, 2)
        if data_value <= dac_velocity_thd["min"] or data_value >= dac_velocity_thd["max"]:
            data_class = "data_warning"        
    elif col == "surf_velocity":
        data_value = round(data_value, 2)
        if data_value <= surf_velocity_thd["min"] or data_value >= surf_velocity_thd["max"]:
            data_class = "data_warning"  
    elif col == "glider_sog":
            data_value = str(round(data_value,2)) + " | " + str(round(data_value * 3600 /1000, 2))
    elif col in ctrl_parameters_int or col in ctrl_parameters_float or col in ctrl_parameters_str:
        if i+1 < len(df):            
            if df.loc[i,col] != df.loc[i+1,col]:
                data_class = "data_change"
        if col in ctrl_parameters_int:
            data_value = int(round(data_value, 0))
        elif col in ctrl_parameters_float:
            data_value = round(data_value, 3)
        else:
            pass
    elif col in gps_locations:
        data_value = f"{round(data_value, 3):.3f}"
    elif col in velocities:
        data_value = f"{round(data_value, 2):.2f}"
    elif col in headings:
        data_value = int(round(data_value, 0))
    elif col == "glider_dive_time":
        data_value = str(int(data_value)) + " | " + str(int(data_value/60.0)) + " | " + str(round(data_value/60.0/60.0, 1))
    elif col == "depth_reached":
        data_value = int(round(data_value, 0))
    elif col in ecurrents:
        data_value = int(round(data_value, 0))
    elif col in adrates:
        data_value = f"{round(data_value, 1):.1f}"
    elif col == "vbd_rate_apogee":
        if data_value <= vbd_rate_thd["min"] or data_value >= vbd_rate_thd["max"]:
            data_class = "data_warning" 
        data_value = f"{round(data_value, 2):.2f}"
    elif col == "vbd_i_apogee":
        if data_value <= vbd_imax_thd["min"] or data_value >= vbd_imax_thd["max"]:
            data_class = "data_warning" 
        data_value = int(round(data_value, 0))
    elif col == "roll_imax":
        if data_value <= roll_imax_thd["min"] or data_value >= roll_imax_thd["max"]:
            data_class = "data_warning" 
        data_value = int(round(data_value, 0))   
    elif col == "pitch_imax":
        if data_value <= pitch_imax_thd["min"] or data_value >= pitch_imax_thd["max"]:
            data_class = "data_warning" 
        data_value = int(round(data_value, 0)) 
    elif col == "vbd_imax":
        if data_value <= vbd_imax_thd["min"] or data_value >= vbd_imax_thd["max"]:
            data_class = "data_warning" 
        data_value = int(round(data_value, 0))   
    elif col in "log_energy_thisdive":
        data_value = f"{round(data_value, 4):.4f}"
    # insert here a new elif for new columns
    else:
        pass
    

    return data_value, data_class


# based on the parameter assign units to show in header
def get_header_units(j):
    units = ""

    if j in ['gps_lat_start', 'gps_lon_start', 'gps_lat_end', 'gps_lon_end']:
        units = "[dd.ddd]"
    elif j == "int_Humidity":
        units = "[%]"
    elif j == "int_Pressure":
        units = "[psi]" 
    elif j == "int_Temperature":
        units = "[" + chr(176) + "C]"
    elif j == "SM_angle":
       units = "[" + chr(176) + "]"
    elif j == "SM_depth":
       units = "[m]"
    elif j in ['dac_velocity', 'surf_velocity' ]:
       units = "[m/s]"
    elif j in ['dac_heading', 'surf_heading', 'glider_hdg']:
       units = "[" + chr(176) + "]"
    elif j == "glider_dive_time":
       units = "[s][min][h]"
    elif j == "glider_dog":
       units = "[km]"
    elif j == "glider_sog":
        units = "[m/s][km/h]"
    elif j in ["roll_imax", "pitch_imax", "vbd_imax", "vbd_i_apogee"]:
        units = "[mA]"
    elif j in ["roll_rate_min", "pitch_rate_min", "vbd_rate_min", "vbd_rate_apogee"]:
        units = "[AD/s]"
    elif j == "depth_reached":
       units = "[m]"
    # add an elif for new columns
    else:
        pass
    
    return units