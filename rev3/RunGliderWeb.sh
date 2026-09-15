#!/bin/ksh

echo -e "\n#######################################################################################\n"

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Print timestamp
echo "[$TIMESTAMP] Starting Glider web script."

cd GLIDERWEB2

echo -e "\n> Activating virtual environment\n"
source .venv-sg/bin/activate

# Reset the bash built-in SECONDS variable to 0
SECONDS=0

echo -e "\n> Starting data processing...\n"
python3 make_db.py

# check if a new status csv file was sent to aoml.glider@gmail.com
echo -e "\n> checking gmail for status table...\n"
python3 get_status.py

echo -e "\n> Starting website build...\n"
python3 build_site.py

# Calculate hours, minutes, and seconds from the SECONDS variable
hours=$((SECONDS / 3600))
minutes=$(( (SECONDS % 3600) / 60 ))
seconds=$((SECONDS % 60))

echo -e "\n====================================="
printf "> Total runtime: %02d:%02d:%02d\n" $hours $minutes $seconds
echo -e "\n=====================================\n"


echo -e "\n> Sending website to phodnet webserver...\n"
SECONDS=0

python3 send_website.py

hours=$((SECONDS / 3600))
minutes=$(( (SECONDS % 3600) / 60 ))
seconds=$((SECONDS % 60))

echo -e "\n====================================="
printf "> Total copy runtime: %02d:%02d:%02d\n" $hours $minutes $seconds
echo -e "\n=====================================\n"


deactivate
echo -e "\n> Virtual environment deactivated\n\n"