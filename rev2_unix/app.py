from flask import Flask, render_template, url_for
from ncmodules import files, logstats, map_html, plots_html, table_html, home_html
import sgid_list as sg
import pandas as pd


# ATTENTION: databases need to be up to date as this app reads from them
# Use @app.route("/plots_<sgid>/") for freezing, otherwise remove the trailing slash '/'

# create flask instance object 'app'
app = Flask(__name__)

# Create website for only seaglider IDs in sgid_list
# sgid_list = ["609", "668"]
sgid_list = sg.sgids


# root page
@app.route("/")
@app.route("/home.html")
@app.route("/index.html")
def home():
    numDivesSummary = 50 # show only about a week of dives
    summary_df = pd.DataFrame() # empty dataframe
    
    # loop ids and get dataframe summary stats from last dives
    for id in sgid_list:
        thisid_dict = home_html.get_stat_summary(id) # returns a summary of the last dive for each glider        
        thisid_df = pd.DataFrame(thisid_dict,index=[0])  # convert dictionary to dataframe
        summary_df = pd.concat([summary_df, thisid_df]) # concatenate dataframes, one row per glider

    summary_html = home_html.glider_summary_html(summary_df)

    # loop an extract last numDivesSummary dives of each glider
    df_list = [] # store dataframes in list
    for id in sgid_list:
        latest_df = home_html.get_latest_dives(id, numDivesSummary)
        df_list.append(latest_df)

    # create folium map with latest dive info
    fname = home_html.make_summary_map(df_list)
    # map_url = url_for('static', filename = fname)
    # print("filename: ",map_html)
    # print last updated time for navigation bar
    proccess_time = home_html.get_processed_time()
    
    return render_template("home_template.html", sgid_list=sgid_list, summary_html=summary_html, proccess_time=proccess_time, fname=fname, homeFlag=True)

# home website for each seaglider
@app.route("/table_<sgid>.html")
def table(sgid=sgid_list[0]): # use first in list if none selected
    print("========TABLE========")
    # check if ID is in list
    if sgid in sgid_list:        
        print(f"Creating {sgid} table")
        dbname = sgid + ".db"
        logtable = "log_table" # table in nnn.db        
        df = files.read_database(dbname, logtable, "descending") # query db in descending dive num order to have last dive first    
        table_data = table_html.convert_to_table(df) # Returns html string for table. use |safe keyword in html template so jinja doesn't change characters in strings
    else:
        table_data = "<div> Glider ID not processed </div>"

    proccess_time = home_html.get_processed_time()
    
    return render_template("logtable_template.html", table_data=table_data, sgid=sgid, sgid_list=sgid_list, proccess_time=proccess_time, homeFlag=False)


# website for seaglider maps
@app.route("/map_<sgid>.html")
def map(sgid=sgid_list[0]):
    print("========MAP==========")
    if sgid in sgid_list:        
        print(f"Creating {sgid} map")
        dbname = sgid + ".db"
        logtable = "log_table"
        df = files.read_database(dbname, logtable, "descending")
        # get navigation dashboard values
        dashvalues = logstats.glider_stats(df)
        navigation_html = logstats.get_navigation_html(dashvalues)    
        # get map object
        fname = map_html.create_map(sgid, df)
        # map_url = url_for('static', filename = fname)
        # map_url = f"static/{fname}"        
    else:
        fname = "<div> Glider ID not processed </div>"
        navigation_html = "<div> Glider ID not processed </div>"

    proccess_time = home_html.get_processed_time()

    return render_template("map_template.html", sgid=sgid, fname=fname, navigation_html=navigation_html, sgid_list=sgid_list, 
                           proccess_time=proccess_time, homeFlag=False)
    # return map_html_str
    #return send_from_directory('static', mapfile)


@app.route("/stats_<sgid>.html")
def stats(sgid=sgid_list[0]): # use first in list if none selected
    print("=======STATS=========")
    # check if ID is in list
    if sgid in sgid_list:        
        print(f"Creating {sgid} stats")
        dbname = sgid + ".db"
        logtable = "log_table" # table in nnn.db
        df = files.read_database(dbname, logtable, "descending") # query db in descending dive num order to have last dive first    
        # table_data = df_html.convert_to_table(df) # Returns html string for table. use |safe keyword in html template so jinja doesn't change characters in strings
        dashvalues = logstats.glider_stats(df) # function to return stats information and plots 
    
        navigation_dash = logstats.get_navigation_html(dashvalues)
        call_dash = logstats.get_call_html(dashvalues)
        health_dash = logstats.get_health_html(dashvalues)
        error_dash = logstats.get_error_html(dashvalues)
        rates_dash = logstats.get_rates_html(dashvalues)
    else:
        navigation_dash = "<div> Glider ID not processed </div>"
        call_dash = "<div> Glider ID not processed </div>" 
        health_dash = "<div> Glider ID not processed </div>"
        error_dash = "<div> Glider ID not processed </div>"
        rates_dash = "<div> Glider ID not processed </div>"

    proccess_time = home_html.get_processed_time()

    return render_template("glider_template.html", sgid=sgid, navigation_dash=navigation_dash, call_dash=call_dash, 
                           health_dash=health_dash, error_dash=error_dash, rates_dash=rates_dash, sgid_list=sgid_list, 
                           proccess_time=proccess_time, homeFlag=False)


# website for seaglider mapping
@app.route("/plots_<sgid>.html")
def plots(sgid=sgid_list[0]):
    print("========PLOTS========")
    if sgid in sgid_list:
        print(f"Creating {sgid} plots")
        dbname = sgid + ".db"
        logtable = "log_table"
        df = files.read_database(dbname, logtable, "descending")
        
        # plots_url = plots_html.plot_line(sgid)
        fname_health = plots_html.plot_health(df, sgid)
        # health_url = url_for('static', filename = fname_health)

        fname_rates = plots_html.plot_rates(df, sgid)
        # rates_url = url_for('static', filename = fname_rates)

        fname_calls = plots_html.plot_calls(df, sgid)
        # calls_url = url_for('static', filename = fname_calls)

        fname_nav = plots_html.plot_navigation(df, sgid)
        # nav_url = url_for('static', filename = fname_nav)

        fname_navpolar = plots_html.plot_navpolar(df, sgid)
        # navpolar_url = url_for('static', filename = fname_navpolar)
               
    else:
        fname_health = "<div> Glider ID not processed </div>"
        fname_rates = "<div> Glider ID not processed </div>"
        fname_calls = "<div> Glider ID not processed </div>"
        fname_nav = "<div> Glider ID not processed </div>"
        fname_navpolar = "<div> Glider ID not processed </div>"
    
    proccess_time = home_html.get_processed_time()

    return render_template("plots_template.html", sgid=sgid, health_plot=fname_health, rates_plot=fname_rates,
                            calls_plot=fname_calls, navigation_plot=fname_nav, navpolar_plot=fname_navpolar, 
                            sgid_list=sgid_list, proccess_time=proccess_time, homeFlag=False)




# test, plots directly from dataframe
# @app.route("/dftable")
# def df_table(sgid="668"):
#     dbname = sgid + ".db"
#     logtable = "log_table"
#     df = files.read_database(dbname, logtable, "descending")
#     df_html = df.to_html(classes='data-table')

#     return render_template("dftable.html", table = df_html, sgid_list=sgid_list, sgid=sgid)


if __name__ == '__main__':
    app.run(debug=True)