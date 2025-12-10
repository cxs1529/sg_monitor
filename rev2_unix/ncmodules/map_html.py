import folium
import pandas as pd



def create_map(sgid, df):
    current_lat = df.loc[0,"gps_lat_end"]
    current_lon = df.loc[0,"gps_lon_end"]
    current_pos = [current_lat,current_lon]
    
    filename = make_summary_map(df, sgid, current_pos)
    
    return filename


def create_map_old(sgid, df):
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
        

    # save map as html
    filename = f"maps/sg{sgid}_map.html"
    m.save("static/" + filename)
    
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