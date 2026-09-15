# ncmodules/status_html.py

def generate_status_table(df):
    """Converts a pandas DataFrame (from status.csv) into a styled HTML table string."""
    if df is None or df.empty:
        return '<div style="margin: 10px 20px 30px 20px;">No status data available.</div>\n'

    html = '<div style="overflow-x:auto; margin: 10px 20px 30px 20px;">\n'
    html += '<table class="status-table">\n'
    
    # Generate headers dynamically from DataFrame columns
    html += '<tr>\n'
    for col in df.columns:
        html += f'<th>{col}</th>\n'
    html += '</tr>\n'
    
    # Generate rows dynamically
    for _, row in df.iterrows():
        html += '<tr>\n'
        
        # Use enumerate to track the column index (i)
        for i, col in enumerate(df.columns):
            # Convert cell to string and replace newlines/carriage returns with a single space
            cell_value = str(row[col]).replace('\n', ' ').replace('\r', ' ')
            
            # Start building the properties for this <td>
            classes = []
            styles = []
            
            # 1. If it's the first column, make the text bold AND left-aligned
            if i == 0:
                styles.append("font-weight: bold;")
                styles.append("text-align: left;")
                
            # 2. If the column header is "Note" or "Notes", apply the left-align text class
            if str(col).strip().lower() in ["note", "notes"]:
                classes.append("text-left")
                
            # Format the HTML attributes if they exist
            class_str = f' class="{" ".join(classes)}"' if classes else ""
            style_str = f' style="{" ".join(styles)}"' if styles else ""
            
            html += f'<td{class_str}{style_str}>{cell_value}</td>\n'
                
        html += '</tr>\n'
        
    html += '</table>\n</div>\n'
    return html