import eel
from live_calc import calc_parser
import time
import os
from importlib.resources import files

WEB_DIR = files('live_calc').joinpath('web')
SAVE_DIR = './saves'

# Start eel
eel.init(WEB_DIR, allowed_extensions=['.js', '.html'])

# List files in save directory
@eel.expose
def get_file_names():
    files = os.listdir(SAVE_DIR)
    # Sort by modified datetime
    files.sort(key=lambda x: -os.path.getmtime(SAVE_DIR + "/" + x))
    return files

# Return file text given path
@eel.expose
def get_file_text(file_path):
    with open(SAVE_DIR + '/' + file_path, 'r') as file:
        return file.read()

# Saves a file given the path and text
@eel.expose
def save_file_text(file_path, text):
    with open(SAVE_DIR + '/' + file_path, 'w') as file:
        return file.write(text)

# Send the input from javascript to python
# Writes output back into javascript through eel
@eel.expose
def send_input(input_string):

    output = ""
    context = None
    error = False
    time_elapsed = 0.0

    # Time execution
    start_time = time.time()

    # Parse, calculate and store output
    output, context, error = calc_parser.parse(input_string, True)
    time_elapsed = time.time() - start_time

    # If there's an error, set the error text
    # if error != None:
    #    error = True
    
    # Set diagnostics
    eel.set_timer(round(time_elapsed * 1000))
    if(context != None):
        eel.set_var_num(len(context))

    # Write the output
    eel.write_output(output, error)

# Start the app
eel.start('app.html', size=(700, 500), port=0)