import folium
from folium.plugins import MeasureControl
# import pandas as pd



def create_map(sgid, df):
    # create map object
    current_lat = df.loc[0,"gps_lat_end"]
    current_lon = df.loc[0,"gps_lon_end"]
    m = folium.Map(location=[current_lat, current_lon], zoom_start=8)

    # current target
    tgt_lat = df.loc[0,"TGT_lat"]
    tgt_lon = df.loc[0,"TGT_lon"]
    tgt_name = df.loc[0,"TGT_name"]
    folium.CircleMarker(
        location=[tgt_lat, tgt_lon],  # Latitude and Longitude
        radius=12,                      # Radius in pixels
        color='white',                   # Outline color
        fill=True,                      # Fill the circle
        fill_color="red",              # Fill color
        fill_opacity=0.6,               # Fill opacity
        popup=f"TGT : {tgt_name}",           # Popup text on click
        tooltip=f"TGT : {tgt_name} | {round(tgt_lat,3)},{round(tgt_lon,3)}"     # Tooltip text on hover
    ).add_to(m)

    # loop through end-of-dive positions
    for i in range(0, len(df)):
        thisdive_lat = df.loc[i,"gps_lat_end"]
        thisdive_lon = df.loc[i,"gps_lon_end"]
        fcolor = "yellow"
        rad = 4

        if i == 0:
            fcolor = "magenta"
            rad = 8

        # create circle marker for each target
        folium.CircleMarker(
            location=[thisdive_lat, thisdive_lon],  # Latitude and Longitude
            radius=rad,                      # Radius in pixels
            color='black',                   # Outline color
            fill=True,                      # Fill the circle
            fill_color=fcolor,              # Fill color
            fill_opacity=0.6,               # Fill opacity
            popup=f"dive: {i}",           # Popup text on click
            tooltip=f"{round(thisdive_lat,3)},{round(thisdive_lon,3)}"     # Tooltip text on hover
        ).add_to(m)
        
    # add measurement tool
    m.add_child(MeasureControl())

    # save map as html
    filename = f"maps/sg{sgid}_map.html"
    m.save("static/" + filename)
    
    return filename