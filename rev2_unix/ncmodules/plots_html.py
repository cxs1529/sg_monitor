import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# def plot_line(sgid):
#     fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])

#     plot_file = f"static/plots/sg{sgid}_plots.html"
#     fig.write_html(plot_file)

#     return plot_file

def plot_health(df, sgid):

    # Create figure with subplots
    health_fig = make_subplots(rows=6, cols=2, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.025, horizontal_spacing=0.01, column_widths=[0.9, 0.1])

    # Add traces to figure
    health_fig.add_trace(go.Scatter(x=df["dive"], y=df["int_Humidity"], mode="lines", line_color="red", name="int_Humidity"), row=1, col=1) # mode="lines+markers"
    health_fig.add_trace(go.Box(y=df["int_Humidity"], name="", showlegend=False, line_color="red"), row=1, col=2)
    health_fig.add_trace(go.Scatter(x=df["dive"], y=df["int_Pressure"], mode="lines", line_color="green", name="int_Pressure"), row=2, col=1)
    health_fig.add_trace(go.Box(y=df["int_Pressure"], name="", showlegend=False, line_color="green"), row=2, col=2)
    health_fig.add_trace(go.Scatter(x=df["dive"], y=df["int_Temperature"], mode="lines", line_color="blue", name="int_Temperature"), row=3, col=1)
    health_fig.add_trace(go.Box(y=df["int_Temperature"], name="", showlegend=False, line_color="blue"), row=3, col=2)
    health_fig.add_trace(go.Scatter(x=df["dive"], y=df["log_24_minv"], mode="lines", line_color="magenta", name="24_minv"), row=4, col=1)
    health_fig.add_trace(go.Box(y=df["log_24_minv"], name="", showlegend=False, line_color="magenta"), row=4, col=2)
    # mfig.add_trace(go.Scatter(x=df["dive"], y=df["log_10_minv"], mode="lines", line=dict(dash='dash', color="rgb(255,50,50)", width=1), name="10_minv"), row=4, col=1)
    # mfig.add_trace(go.Box(y=df["log_10_minv"], name="10_minv", showlegend=False), row=4, col=2)
    health_fig.add_trace(go.Scatter(x=df["dive"], y=df["depth_reached"], mode="lines", line_color="brown", name="depth_reached"), row=5, col=1)
    # Battery capacity
    batteryPercent_df = (df["log_AH_total_capacity"] - df["log_AH_total_consumed"])/df["log_AH_total_capacity"]
    batteryUsed_thisdive_df = df["log_energy_thisdive"] # Normalize relative to 4.7Wh at 15V energy, required by the average 900m dive
    health_fig.add_trace(go.Scatter(x=df["dive"], y=batteryPercent_df*100, line_color="black", mode="lines", name="batteryPercent"), row=6, col=1)
    health_fig.add_trace(go.Scatter(x=df["dive"], y=batteryUsed_thisdive_df*550, mode="markers", marker_color="grey", name="dive_AHx550"), row=6, col=1)

    # Update figure properties
    health_fig.update_layout(height=600, width=1200, title_text="<b>Health Stats</b>", title_x=0.5)

    # Update x-axis properties
    # mfig.update_xaxes(title_text="Dive", range=[0, 220], row=5, col=1)

    # Update y-axis properties
    health_fig.update_yaxes(title_text="RH%", row=1, col=1)
    health_fig.update_yaxes(title_text="PSI", row=2, col=1)
    health_fig.update_yaxes(title_text="°C", row=3, col=1)
    health_fig.update_yaxes(title_text="V", row=4, col=1)
    health_fig.update_yaxes(title_text="m", row=5, col=1)
    health_fig.update_yaxes(title_text="%", row=6, col=1)

    health_fig.update_xaxes(title_text="Dive", row=6, col=1)

    # Remove col 2 y-axis
    health_fig.update_yaxes(showticklabels=False, col=2)
   
    fname = f"plots/sg{sgid}_health_plot.html"
    health_fig.write_html("static/" + fname)

    return fname


def plot_rates(df, sgid):

    rates_fig = make_subplots(rows=8, cols=2, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.025, horizontal_spacing=0.01, column_widths=[0.9, 0.1])
    # roll
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["roll_imax"], mode="lines", line_color="red", name="roll_imax"), row=1, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["roll_imax"], name="", showlegend=False, line_color="red"), row=1, col=2)
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["roll_rate_min"], mode="lines",line=dict(dash='dash', color="red"), name="roll_rate_min"), row=2, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["roll_rate_min"], name="", showlegend=False, line_color="red"), row=2, col=2)
    # pitch
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["pitch_imax"], mode="lines", line_color="blue", name="pitch_imax"), row=3, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["pitch_imax"], name="", showlegend=False, line_color="blue"), row=3, col=2)
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["pitch_rate_min"], mode="lines", line=dict(dash='dash', color="blue"), name="pitch_rate_min"), row=4, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["pitch_rate_min"], name="", showlegend=False, line_color="blue"), row=4, col=2)
    # VBD
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["vbd_i_apogee"], mode="lines", line_color="green", name="vbd_i_apogee"), row=5, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["vbd_i_apogee"], name="", showlegend=False, line_color="green"), row=5, col=2)
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["vbd_rate_apogee"], mode="lines", line=dict(dash='dash', color="green"), name="vbd_rate_apogee"), row=6, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["vbd_rate_apogee"], name="", showlegend=False, line_color="green"), row=6, col=2)
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["vbd_rate_min"], mode="lines", line=dict(dash='dot', color="green"), name="vbd_rate_min"), row=7, col=1) # mode="lines+markers"
    rates_fig.add_trace(go.Box(y=df["vbd_rate_min"], name="", showlegend=False, line_color="green"), row=7, col=2)
    # depth
    rates_fig.add_trace(go.Scatter(x=df["dive"], y=df["depth_reached"], mode="lines", line_color="brown", name="depth_reached"), row=8, col=1)

    rates_fig.update_yaxes(title_text="mA", row=1, col=1)
    rates_fig.update_yaxes(title_text="AD/s", row=2, col=1)
    rates_fig.update_yaxes(title_text="mA", row=3, col=1)
    rates_fig.update_yaxes(title_text="AD/s", row=4, col=1)
    rates_fig.update_yaxes(title_text="mA", row=5, col=1)
    rates_fig.update_yaxes(title_text="AD/s", row=6, col=1)
    rates_fig.update_yaxes(title_text="AD/s", row=7, col=1)
    rates_fig.update_yaxes(title_text="m", row=8, col=1)

    rates_fig.update_yaxes(showticklabels=False, col=2)

    rates_fig.update_xaxes(title_text="Dive", row=8, col=1)

    rates_fig.update_layout(height=800, width=1200, title_text="<b>Rates Stats</b>", title_x=0.5)

    fname = f"plots/sg{sgid}_rates_plot.html"
    rates_fig.write_html("static/" + fname)

    return fname  



def plot_calls(df, sgid):

    call_fig = make_subplots(rows=4, cols=2, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.01, horizontal_spacing=0.01, column_widths=[0.9, 0.1])
    # calls
    call_fig.add_trace(go.Bar(x=df["dive"], y=df["CALLS"], name="CALLS", marker=dict(color='red')), row=1, col=1) # mode="lines+markers"
    call_fig.add_trace(go.Box(y=df["CALLS"], name="", showlegend=False, line_color="red"), row=1, col=2)
    # call depth
    call_fig.add_trace(go.Scatter(x=df["dive"], y=df["SM_depth"], mode="lines", line_color="blue", name="SM_depth"), row=2, col=1) # mode="lines+markers"
    call_fig.add_trace(go.Box(y=df["SM_depth"], name="", showlegend=False, line_color="blue"), row=2, col=2)
    # call angle
    call_fig.add_trace(go.Scatter(x=df["dive"], y=df["SM_angle"], mode="lines", line_color="green", name="SM_angle"), row=3, col=1) # mode="lines+markers"
    call_fig.add_trace(go.Box(y=df["SM_angle"], name="", showlegend=False, line_color="green"), row=3, col=2)
    # smcc
    call_fig.add_trace(go.Scatter(x=df["dive"], y=df["SM_CC"], mode="lines", line_color="black", name="SM_CC"), row=4, col=1) # mode="lines+markers"
    call_fig.add_trace(go.Box(y=df["SM_CC"], name="", showlegend=False, line_color="black"), row=4, col=2)

    call_fig.update_yaxes(title_text="calls", row=1, col=1)
    call_fig.update_yaxes(title_text="m", row=2, col=1)
    call_fig.update_yaxes(title_text="°", row=3, col=1)
    call_fig.update_yaxes(title_text="SMCC", row=4, col=1)

    call_fig.update_yaxes(showticklabels=False, col=2)

    call_fig.update_xaxes(title_text="Dive", row=4, col=1)

    call_fig.update_layout(height=400, width=1200, title_text="<b>Call Stats</b>", title_x=0.5)

    fname = f"plots/sg{sgid}_calls_plot.html"
    call_fig.write_html("static/" + fname)

    return fname    


def plot_navigation(df, sgid):

    nav_fig = make_subplots(rows=5, cols=2, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.01, horizontal_spacing=0.01, column_widths=[0.9, 0.1])

    nav_fig.add_trace(go.Scatter(x=df["dive"], y=df["MAX_BUOY"], mode="lines", line_color="red", name="MAX_BUOY"), row=1, col=1)
    nav_fig.add_trace(go.Scatter(x=df["dive"], y=df["glider_dog"], mode="lines", line_color="blue", name="glider_dog"), row=2, col=1)
    nav_fig.add_trace(go.Scatter(x=df["dive"], y=df["glider_sog"], mode="lines", line_color="green", name="glider_sog"), row=3, col=1)
    nav_fig.add_trace(go.Scatter(x=df["dive"], y=df["dac_velocity"], mode="lines", line_color="black", name="dac_velocity"), row=4, col=1)
    nav_fig.add_trace(go.Scatter(x=df["dive"], y=df["surf_velocity"], mode="lines", line_color="grey", name="surf_velocity"), row=5, col=1)

    nav_fig.update_yaxes(title_text="CC", row=1, col=1)
    nav_fig.update_yaxes(title_text="km", row=2, col=1)
    nav_fig.update_yaxes(title_text="m/s", row=3, col=1)
    nav_fig.update_yaxes(title_text="m/s", row=4, col=1)
    nav_fig.update_yaxes(title_text="m/s", row=5, col=1)

    nav_fig.update_yaxes(showticklabels=False, col=2)

    nav_fig.update_xaxes(title_text="Dive", row=5, col=1)

    nav_fig.update_layout(height=500, width=1200, title_text="<b>Navigation Stats</b>", title_x=0.5)

    fname = f"plots/sg{sgid}_navigation_plot.html"
    nav_fig.write_html("static/" + fname)

    return fname 


def plot_navpolar(df, sgid):
    polar_fig = go.Figure()
    polar_fig.add_trace(go.Scatterpolar(r=df["glider_sog"], theta=df["glider_hdg"], mode="markers", name="glider_sog", hovertext=df["dive"]))
    polar_fig.add_trace(go.Scatterpolar(r=df["dac_velocity"], theta=df["dac_heading"], mode="markers", name="dac_velocity", hovertext=df["dive"]))
    polar_fig.add_trace(go.Scatterpolar(r=df["surf_velocity"], theta=df["surf_heading"], mode="markers", name="surf_velocity", hovertext=df["dive"]))

    polar_fig.update_layout(height=600, width=600, title_text="<b>Navigation Polar</b>", title_x=0.5)

    fname = f"plots/sg{sgid}_navpolar_plot.html"
    polar_fig.write_html("static/" + fname)

    return fname