
# define warning threshold values for conditional formatting
# health
int_Humidity_thd = {"min":40.0, "max": 70.0}
int_Pressure_thd = {"min":9.2, "max": 10.0}
int_Temperature_thd = {"min":15, "max": 35}
battery_volt_thd = {"min":12.5, "max": 16}
battery_percent_thd = {"min":0.5, "max": 1}
# calls
SM_angle_thd = {"min": 55, "max": 90}
SM_depth_thd = {"min":0.5, "max": 1.2}
CALLS_thd = {"min":0, "max": 3}
# navigation
dac_velocity_thd = {"min":0, "max": 1}
surf_velocity_thd = {"min":0, "max": 1} 
dog_thd = {"min": 1.5, "max": 4} # km
sog_thd = {"min": 0.1, "max": 1} # m/s
# rates
vbd_rate_thd = {"min": 3.5, "max": 4.7} 
vbd_imax_thd = {"min": 1000, "max": 2500} 
pitch_rate_thd = {"min": 150, "max": 400}
pitch_imax_thd = {"min": 50, "max": 350} 
roll_rate_thd = {"min": 500, "max": 700} 
roll_imax_thd = {"min": 20, "max": 120} 
# errors
error_thd = {"min": 0, "max": 1}
retry_thd = {"min": 0, "max": 3}