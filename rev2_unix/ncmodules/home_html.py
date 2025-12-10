from .logstats import glider_stats, ztime
from .files import read_database
import pandas as pd
from datetime import datetime, timezone
import folium

def get_stat_summary(sgid):
    print("=======SUMMARY=======")
    print(f"Creating {sgid} summary")
    dbname = sgid + ".db"
    logtable = "log_table" # table in nnn.db    
    df = read_database(dbname, logtable, "descending")
    sg_dict = glider_stats(df) # returns dataframe values for the last dive only
    sg_dict["sgid"] = sgid
    
    return sg_dict

# Create a grid for each glider
def glider_summary_html(df):

    i = 0
    sgstr = ""    
    for row in df.itertuples(index=True, name='PandasRow'):       

        idstr = f"<div class='summary-div'>\n <h3>ID</h3>\n <p class='p-normal'>{row.sgid}</p>\n </div>\n"
        divestr = f"<div class='summary-div'>\n <h3>DIVE</h3>\n <p class='p-normal'>{row.dive}</p>\n </div>\n"
        timestr = f"<div class='summary-div'>\n <h3>TIME</h3>\n <p class='p-normal'>{ztime(row.time_end)} ({(elapsed(row.time_end)):.1f} h ago)</p>\n </div>\n"
        posstr = f"<div class='summary-div'>\n <h3>POSITION</h3>\n <p class='p-normal'>{(row.gps_lat_end):.3f},{(row.gps_lon_end):.3f}</p>\n </div>\n"
        tgtstr = f"<div class='summary-div'>\n <h3>TARGET</h3>\n <p class='p-normal'>{row.TGT_name}<br>{(row.TGT_lat):.3f},{(row.TGT_lon):.3f}<br>{(row.tgt_distance):.1f} km<br>{(row.tgt_time/24.0):.1f} days</p>\n </div>\n"
        humidstr = f"<div class='summary-div'>\n <h3>HUMIDITY</h3>\n <p class='p-normal'>{(row.int_Humidity):.1f}</p>\n </div>\n"
        tempstr = f"<div class='summary-div'>\n <h3>TEMPERATURE</h3>\n <p class='p-normal'>{(row.int_Temperature):.1f}</p>\n </div>\n"
        presstr = f"<div class='summary-div'>\n <h3>PRESSURE</h3>\n <p class='p-normal'>{(row.int_Pressure):.2f}</p>\n </div>\n"
        voltstr = f"<div class='summary-div'>\n <h3>VOLTAGE</h3>\n <p class='p-normal'>10V: {(row.log_10_minv):.1f}<br>24V: {(row.log_24_minv):.1f}</p>\n </div>\n"
        energystr = f"<div class='summary-div'>\n <h3>BATTERY</h3>\n <p class='p-normal'>{(row.batteryPercent*100):.1f} %<br>{(row.battery_ndives):.0f} dives </p>\n </div>\n"

        sgstr = sgstr + f"<div class=\"sg{i}-container\">\n" + idstr + divestr + timestr + posstr + tgtstr + humidstr + tempstr + presstr + voltstr + energystr + "</div>\n"
        i = i+1

    html_summary = "<div class=\"summary-section\">\n" + sgstr + "</div>\n"
    return html_summary
    
    
def elapsed(dt):
    dt = dt.replace("Z","")
    dt = dt.split("T")
    dt_date = dt[0].split("-")
    y = dt_date[0]
    m = dt_date[1]
    d = dt_date[2]
    
    dt_time = dt[1].split(":")
    h = dt_time[0]
    mm = dt_time[1]
    s = dt_time[2]

    end_dive_time = datetime(int(y), int(m), int(d), int(h), int(mm), int(s), tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc) 
    elapsed_time = (current_time.timestamp() - end_dive_time.timestamp())/3600.0 # in h

    return elapsed_time


def get_processed_time():
    process_time = datetime.now(timezone.utc)
    timestr = process_time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = "Last Updated " + timestr + " UTC"
    return timestamp

# extracts last N dives of each dataframe
def get_latest_dives(sgid, count):
    dbname = sgid + ".db"
    logtable = "log_table" # table in nnn.db
    df = read_database(dbname, logtable, "descending")
    df_10 = df.head(count) # get latest N=count dives
    df_10["sgid"] = sgid

    return df_10

# creates map with all the gliders, condireting last N dives
def make_summary_map(df_list):
    init_pos = [20.416501, -69.914840]
    full_map = folium.Map(location=init_pos, zoom_start=6)

    # loop through list of df for each glider and create map objects
    for df in df_list:
        
        for i in range(0, len(df)):
            # extract reelvant values
            lat = df.loc[i,"gps_lat_end"]
            lon = df.loc[i,"gps_lon_end"]
            dive = df.loc[i,"dive"]
            sgid = df.loc[i,"sgid"]
            depth = df.loc[i,"depth_reached"]
            sog = df.loc[i,"glider_sog"]
            dog = df.loc[i,"glider_dog"]

            # format to plot in map
            popup_text = f"id: {sgid}<br>dive: {dive}<br>position: {(lat):.3f},{(lon):.3f}<br>depth: {(depth):.0f} m<br>sog: {(sog):.1f} m/s<br>dog: {(dog):.1f} km"
            tip_text = f"id: {sgid}<br>dive: {dive}"
            
            # marker properties
            fillcolor = "yellow"
            extcolor = "white"
            radius = 4
            # if last dive, make different
            if i == 0:
                fillcolor = "magenta"
                extcolor = "black"
                radius = 8
                timeend = df.loc[i,"time_end"]
                tip_text = f"id: {sgid}<br>dive: {dive}<br>time: {timeend}"

            # get marker object and add to map
            obj = create_map_marker(lat , lon, radius, extcolor, fillcolor, popup_text, tip_text )
            obj.add_to(full_map)
        
        # add target for last dive only
        tgt_lat = df.loc[0,"TGT_lat"]
        tgt_lon = df.loc[0,"TGT_lon"]
        tgt_name = df.loc[0,"TGT_name"]
        sgid = df.loc[0,"sgid"]
        popup_text=f"id: {sgid}<br>target: {tgt_name}",           # Popup text on click
        tip_text=f"id: {sgid}<br>target: <b>{tgt_name}</b><br> {(tgt_lat):.3f},{(tgt_lon):.3f}"
        extcolor = "white"
        fillcolor = "red"
        radius = 12
        tgt_obj = create_map_marker(tgt_lat , tgt_lon, radius, extcolor, fillcolor, popup_text, tip_text )
        tgt_obj.add_to(full_map)

    # save map as html
    filename = f"maps/home_map.html"
    full_map.save("static/" + filename)

    return filename


def create_map_marker(lat , lon, radius, extcolor, fillcolor, popup_text, tip_text ):

    myobj = folium.CircleMarker(
        location=[lat, lon],  # Latitude and Longitude
        radius=radius,                      # Radius in pixels
        color=extcolor,                   # Outline color
        fill=True,                      # Fill the circle
        fill_color=fillcolor,              # Fill color
        fill_opacity=0.6,               # Fill opacity
        popup=popup_text,           # Popup text on click
        tooltip=tip_text     # Tooltip text on hover
    )

    return myobj