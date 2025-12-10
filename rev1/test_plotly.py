from ncmodules import files
import plotly.express as px

sgid="668"


dbname = sgid + ".db"
logtable = "log_table" # table in nnn.db
df = files.read_database(dbname, logtable, "descending")

print(df)


fig = px.line(df, x="dive", y="int_Humidity")
fig.show()

# health_plot_path = f"static/plots/sg{sgid}_health_plot.html"
# fig.write_html(health_plot_path)

