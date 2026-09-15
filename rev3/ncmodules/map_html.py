import folium
import pandas as pd
import os



def create_map(sgid, df):
    current_lat = df.loc[0,"gps_lat_end"]
    current_lon = df.loc[0,"gps_lon_end"]
    current_pos = [current_lat,current_lon]
    
    filename = make_summary_map(df, sgid, current_pos)
    
    return filename



# creates map with all the gliders, condireting last N dives
def make_summary_map(df, sgid, init_pos):
    #init_pos = [20.416501, -69.914840]
    full_map = folium.Map(location=init_pos, zoom_start=6)
    
    # loop through dataframe and create map objects    
    for i in range(0, len(df)):
        # extract reelvant values
        lat = df.loc[i,"gps_lat_end"]
        lon = df.loc[i,"gps_lon_end"]
        dive = df.loc[i,"dive"]
        #sgid = df.loc[i,"sgid"]
        depth = df.loc[i,"depth_reached"]
        sog = df.loc[i,"glider_sog"]
        dog = df.loc[i,"glider_dog"]

        # format to plot in map (Update JSON link to match padded format)
        dive_padded = f"{int(dive):04d}"
        json_link = f"<br><a href='../json/sg{sgid}{dive_padded}.json' target='_blank'>View Dive JSON</a>"
        popup_text = f"id: {sgid}<br>dive: {dive}<br>position: {(lat):.3f},{(lon):.3f}<br>depth: {(depth):.0f} m<br>sog: {(sog):.1f} m/s<br>dog: {(dog):.1f} km{json_link}"
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
    # end for loop
    
    # add target for last dive only
    tgt_lat = df.loc[0,"TGT_lat"]
    tgt_lon = df.loc[0,"TGT_lon"]
    tgt_name = df.loc[0,"TGT_name"]
    #sgid = df.loc[0,"sgid"]
    popup_text=f"id: {sgid}<br>target: {tgt_name}",           # Popup text on click
    tip_text=f"id: {sgid}<br>target: <b>{tgt_name}</b><br> {(tgt_lat):.3f},{(tgt_lon):.3f}"
    extcolor = "white"
    fillcolor = "red"
    radius = 12
    tgt_obj = create_map_marker(tgt_lat , tgt_lon, radius, extcolor, fillcolor, popup_text, tip_text )
    tgt_obj.add_to(full_map)

    # Make sure target directory exists
    os.makedirs("static/maps", exist_ok=True)

    # save map as html
    filename = f"maps/sg{sgid}_map.html"
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