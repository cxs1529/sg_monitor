## NetCDF file processing and website generation for AUV seaglider pilot monitoring dashboard

### Database creation
Run main_db.py indicating a directory containing glider directories with the respective netcdf files. The script will parse the .nc files and store data into an SQLite database.
If the database exists, it will look for the file and skip its processing if it was already process to improve processing time.

### Website generation
Run run.py to generate the html files based on the database created.
The database must exist to run this script.
This script creates a static website, based in the app.py script based in Flask.

### Example Website
https://cxs1529.github.io/piloting-monitoring/

#### HOME PAGE
![glider_home](https://github.com/user-attachments/assets/d59608e1-598a-4896-8859-0aa928d42b72)

#### GLIDER STATUS PAGE
![glider_dashboard](https://github.com/user-attachments/assets/492b0b3a-6f7d-4fc1-aef0-04ce72ed4394)

#### GLIDER LOG TABLE PAGE
![glider_logtable](https://github.com/user-attachments/assets/05a0c48a-0fe2-4077-af92-5bfd8a8dcf4c)

#### GLIDER MAP PAGE 
![glider_map](https://github.com/user-attachments/assets/6be2d443-e942-479f-a248-f73da66e91ef)

#### GLIDER PLOTS PAGE
![glider_plots](https://github.com/user-attachments/assets/67d74c6a-f7f8-4f22-b8b7-70ab4f860532)

