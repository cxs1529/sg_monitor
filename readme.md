## NetCDF file processing and website generation for AUV seaglider pilot monitoring dashboard
The application creates a static website based on Flask and Flask-freeze.

### Website generation configuration and run steps
1) Edit the *sgid_list.py* file with the source directory containing the .nc files, and the list of seaglider IDs to process.
2) Run *make_db.py* to parse the .nc files and create am sqlite database.
3) Run *make_web.py* to read the database and generate the html files in the designated directory (*websiteDir*).
4) Run *send_website.py* to copy the webpage files to the desired public webserver directory.

### Website generation in one script
Edit the *sgid_list.py* and run the bash scipt: 
All steps indicated above are compiled in RunGliderWeb.sh -> cd to this dir and run ./RunGliderWeb.sh

### Versions
- rev1: original version outdated.
- rev2: latest version working on live webserver.

### Example Website (rev2)
https://cxs1529.github.io/sg_monitor/rev2_unix/static_website/index.html


#### HOME PAGE
![homepage](https://github.com/user-attachments/assets/0723a392-cc59-44c5-b452-68f76737a7c5)
![homepage2](https://github.com/user-attachments/assets/2d37d656-32fc-4e3e-804b-da970b575c51)

#### GLIDER STATUS PAGE
![stats](https://github.com/user-attachments/assets/ba666961-1ff3-4338-ac04-dc2de2c70551)


#### GLIDER LOG TABLE PAGE
![table](https://github.com/user-attachments/assets/34f285f2-db29-45a6-9898-8d1344c8643e)


#### GLIDER MAP PAGE 
![map](https://github.com/user-attachments/assets/353e4c1b-83bb-443a-aeb1-00dd66097780)


#### GLIDER PLOTS PAGE
![plots](https://github.com/user-attachments/assets/1b113887-5d55-43e5-a944-8325bf958e57)


