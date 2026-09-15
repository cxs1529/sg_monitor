import os
import pandas as pd
import shutil
from jinja2 import Environment, FileSystemLoader
from ncmodules import files, logstats, map_html, plots_html, table_html, home_html, status_html
import sgid_list as sg

# Configuration
TEMPLATE_DIR = 'templates'
OUTPUT_DIR = 'static_website'

def main():
    # 1. Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Set up the raw Jinja2 Environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    sgid_list = sg.sgids
    print("Building static website...")

    # ==========================================
    # 3. Build the Home Page (index.html)
    # ==========================================
    print("Generating Home Page...")
    numDivesSummary = 50
    summary_df = pd.DataFrame()
    
    for sgid in sgid_list:
        thisid_dict = home_html.get_stat_summary(sgid)
        thisid_df = pd.DataFrame(thisid_dict, index=[0]) 
        # Using sort=False to ensure compatibility with older pandas versions standard in Py 3.6
        summary_df = pd.concat([summary_df, thisid_df], sort=False) 

    summary_html = home_html.glider_summary_html(summary_df)

    df_list = []
    for sgid in sgid_list:
        latest_df = home_html.get_latest_dives(sgid, numDivesSummary)
        df_list.append(latest_df)

    fname = home_html.make_summary_map(df_list)
    process_time = home_html.get_processed_time()

    # --- Read status.csv from the messages directory ---
    try:
        # Construct the path to messages/status.csv
        status_file_path = os.path.join('messages', 'status.csv')
        
        # Read the CSV (headers are automatically inferred from the first row)
        status_df = pd.read_csv(status_file_path)
        
        # Enforce maximum 20x20 dimension
        status_df = status_df.iloc[:20, :20]
        
        # Drop columns and rows that are completely empty, then fill remaining NaNs
        status_df = status_df.dropna(how='all', axis=0).dropna(how='all', axis=1).fillna("")
    except Exception as e:
        print(f"Error loading {status_file_path}: {e}")
        status_df = pd.DataFrame() # Fallback to empty DataFrame if file is missing

    # Generate status table html from the dataframe
    status_table_html = status_html.generate_status_table(status_df)
    
    # Render template and write to index.html
    home_template = env.get_template("home_template.html")
    home_output = home_template.render(
        sgid_list=sgid_list, 
        summary_html=summary_html, 
        proccess_time=process_time, 
        fname=fname, 
        homeFlag=True,
        status_table_html=status_table_html # pass the status table to html builder
    )
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_output)
        
    # ==========================================
    # 4. Build Glider-Specific Pages
    # ==========================================
    # Pre-load templates
    table_template = env.get_template("logtable_template.html")
    map_template = env.get_template("map_template.html")
    stats_template = env.get_template("glider_template.html")
    plots_template = env.get_template("plots_template.html")

    for sgid in sgid_list:
        print(f"Generating pages for SG{sgid}...")
        dbname = f"{sgid}.db"
        logtable = "log_table"
        
        try:
            # Read DB
            df = files.read_database(dbname, logtable, "descending")
            
            # --- TABLE PAGE ---
            table_data = table_html.convert_to_table(df)
            table_output = table_template.render(
                table_data=table_data, sgid=sgid, sgid_list=sgid_list, 
                proccess_time=process_time, homeFlag=False
            )
            with open(os.path.join(OUTPUT_DIR, f"table_{sgid}.html"), "w", encoding="utf-8") as f:
                f.write(table_output)

            # --- MAP PAGE ---
            dashvalues = logstats.glider_stats(df)
            navigation_html = logstats.get_navigation_html(dashvalues)
            map_fname = map_html.create_map(sgid, df)
            map_output = map_template.render(
                sgid=sgid, fname=map_fname, navigation_html=navigation_html, 
                sgid_list=sgid_list, proccess_time=process_time, homeFlag=False
            )
            with open(os.path.join(OUTPUT_DIR, f"map_{sgid}.html"), "w", encoding="utf-8") as f:
                f.write(map_output)

            # --- STATS PAGE ---
            call_dash = logstats.get_call_html(dashvalues)
            health_dash = logstats.get_health_html(dashvalues)
            error_dash = logstats.get_error_html(dashvalues)
            rates_dash = logstats.get_rates_html(dashvalues)
            stats_output = stats_template.render(
                sgid=sgid, navigation_dash=navigation_html, call_dash=call_dash, 
                health_dash=health_dash, error_dash=error_dash, rates_dash=rates_dash, 
                sgid_list=sgid_list, proccess_time=process_time, homeFlag=False
            )
            with open(os.path.join(OUTPUT_DIR, f"stats_{sgid}.html"), "w", encoding="utf-8") as f:
                f.write(stats_output)

            # --- PLOTS PAGE ---
            fname_health = plots_html.plot_health(df, sgid)
            fname_rates = plots_html.plot_rates(df, sgid)
            fname_calls = plots_html.plot_calls(df, sgid)
            fname_nav = plots_html.plot_navigation(df, sgid)
            fname_navpolar = plots_html.plot_navpolar(df, sgid)
            
            plots_output = plots_template.render(
                sgid=sgid, health_plot=fname_health, rates_plot=fname_rates,
                calls_plot=fname_calls, navigation_plot=fname_nav, navpolar_plot=fname_navpolar, 
                sgid_list=sgid_list, proccess_time=process_time, homeFlag=False
            )
            with open(os.path.join(OUTPUT_DIR, f"plots_{sgid}.html"), "w", encoding="utf-8") as f:
                f.write(plots_output)
                
        except Exception as e:
            print(f"  [!] Error processing SG{sgid} pages: {e}")
            
            # Generate fallback pages if the database fails
            fallback_msg = "<div> Glider ID not processed or Database Missing </div>"
            error_output = table_template.render(table_data=fallback_msg, sgid=sgid, sgid_list=sgid_list, proccess_time=process_time, homeFlag=False)
            with open(os.path.join(OUTPUT_DIR, f"table_{sgid}.html"), "w", encoding="utf-8") as f: 
                f.write(error_output)

    # ==========================================
    # 5. Copy Static Assets (Moved to the end)
    # ==========================================
    dest_static = os.path.join(OUTPUT_DIR, 'static')
    if os.path.exists(dest_static):
        shutil.rmtree(dest_static) # Remove old static folder to ensure fresh files
    shutil.copytree('static', dest_static)
    print(f"Copied static assets (including JSON, Maps, and Plots) to {dest_static}")
    print(f"Complete! Check the '{OUTPUT_DIR}' directory.")

if __name__ == '__main__':
    main()