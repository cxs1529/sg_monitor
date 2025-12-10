# freeze.py
from flask_frozen import Freezer
# Import your Flask app instance and the list of glider IDs from your app.py file
from app import app, sgid_list 

# Initialize Frozen-Flask
freezer = Freezer(app)

# Create "URL generators" for your dynamic routes.
# These functions tell the freezer which specific pages to build.
# The function name must match the view function name in app.py.

@freezer.register_generator
def table():
    # Loop through each glider ID and yield a dictionary
    # specifying the value for the <sgid> variable in the URL.
    for sgid in sgid_list:
        yield {'sgid': sgid}

@freezer.register_generator
def map():
    for sgid in sgid_list:
        yield {'sgid': sgid}

@freezer.register_generator
def stats():
    for sgid in sgid_list:
        yield {'sgid': sgid}

@freezer.register_generator
def plots():
    for sgid in sgid_list:
        yield {'sgid': sgid}

# This is the main part that runs the freezing process
if __name__ == '__main__':
    print("Freezing the Flask application into a static website...")
    # This command builds the static site
    freezer.freeze()
    print("Freezing complete! Your static site is in the 'build' directory.")