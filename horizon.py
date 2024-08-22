import math
import os
from matplotlib import ticker
import numpy as np
import requests
import matplotlib.pyplot as plt

from datetime import datetime, timedelta

# Function to count the number of days between start and end date of your calculation.
def day_counter(start_date,end_date):
    start = datetime.strptime(start_date,"%Y-%m-%d")
    end = datetime.strptime(end_date,"%Y-%m-%d")

    delta = end - start
    print(delta.days)
    return delta.days

# Function to calculate the next date after adding a 90000 days to a given date. Because of day limit of JPL API.
def calculate_next_date(start_date, days_to_add):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    next_date = start_date + timedelta(days=days_to_add)

    print(next_date.strftime("%Y-%m-%d"))
    return next_date.strftime("%Y-%m-%d")

# Function to calculate the number of requests needed based on a JPL API limit of 90000 days.
def calculate_request_count(start_time,stop_time):
    return (day_counter(start_time,stop_time) // 90000) + 1
    
# Function to send a request to the JPL Horizons API for ephemerides data with properties
# It requests with step size of 1 day in cvs format and with just x, y, z coordinates without labels and in km.
# "object_id" is for id of major body, start and stop time is our time interval.
def send_request(object_id,start_time,stop_time):
    url = 'https://ssd.jpl.nasa.gov/api/horizons.api'

    query_url = (
        f"{url}?format=text&COMMAND='{object_id}'&OBJ_DATA='YES'&MAKE_EPHEM='YES'&EPHEM_TYPE='VECTORS'&VEC_TABLE='1'"
        f"&CENTER='500@0'&START_TIME='{start_time}'&STOP_TIME='{stop_time}'&STEP_SIZE='1 d'&VEC_LABELS='NO'&CSV_FORMAT='YES'"
        f"&QUANTITIES='1,9,20,23,24,29'"
    ) # You can change step size with &STEP_SIZE parameter it can take m for minute, h for hour, mo for month, y for year
    # For further spesification for this url you can check https://ssd-api.jpl.nasa.gov/doc/horizons.html
    # For the details of &QUANTITIES parameter check https://ssd.jpl.nasa.gov/horizons/manual.html#output

    print("Query URL:", query_url) # It prints the request url for debugging
    
    return requests.get(query_url)

# Function to append the response from the API to a file with the name of major body for bulk requests.
def append_response_to_file(response,response_filename):
    if response.status_code == 200:
        with open(response_filename, "ab+") as file:
            file.write(response.content)
            print(f"Ephemerides data saved to {response_filename}")
    else:
        print(f"Error: {response.status_code}")

# Function to write the response from the API to a file with the name of major body for single request.
def add_response_to_file(response,response_filename):
    if response.status_code == 200:
        with open(response_filename, "wb+") as file:
            file.write(response.content)
            print(f"Ephemerides data saved to {response_filename}")
    else:
        print(f"Error: {response.status_code}")

# Function to fetch ephemerides data and handle the request splitting if necessary
def fetch_ephemerides(object_id, start_time, stop_time, output_filename):

    response_filename = f"{output_filename}.csv"   

    request_count = calculate_request_count(start_time,stop_time)
    responses = []

    if request_count > 1:
        calc_start_time = start_time
        calc_stop_time = calculate_next_date(start_time,90000)

        for _ in range(request_count - 1): 
            responses.append(send_request(object_id,calc_start_time,calc_stop_time))
            calc_start_time = calculate_next_date(calc_stop_time,1)
            calc_stop_time = calculate_next_date(calc_start_time,90000)
        responses.append(send_request(object_id,calc_start_time,stop_time)) # There is on last separate request because its stop_time specific to your input. It is not calulated
    elif request_count == 1:
        add_response_to_file(send_request(object_id,start_time,stop_time),response_filename) # If only one request is enough it runs only one request with send_request function and write to file.
    else:
        raise ValueError("Illegal date")

    for response in responses:
        append_response_to_file(response, response_filename) # It appends all the responses to a file.

# Function to calculate the difference between ephemerides data from Horizons and your calculations
def calc_ephemerides_diff(horizons_filename,input_filename,output_directory):

    horizons_file = f"{horizons_filename}.csv"
    input_file = f"{input_filename}.dat"
    output_file = f"{output_directory}/differences1y_100s.txt" # You can edit this result file name according to your dates and step size of your calculation
    output_plot = f"{output_directory}/difference_plots1y_100s.png" # You can edit this plot file name according to your dates and step size of your calculation
    
    # They are the lists for the tuples of your coordinates and horizon coordinates
    horizons_coordinates = [] 
    input_coordinates = []

    with open(horizons_file, 'r') as file: # It opens API files with read mode
        horizons_lines = file.readlines()
    
    data_start = False # It is a boolean variable for checking is the data start and finished.
    for line in horizons_lines:
        if line.startswith("$$SOE"): # Start of ephemeris
            data_start = True # It means data start
            continue
        elif line.startswith("$$EOE"): # End of ephemeris
            data_start = False # It means data end
        
        if data_start and line.strip(): # Skip empty lines
                columns = line.split(',') # Separate them with commas because it is csv (comma separated values) file
                if len(columns) >= 5: # Ensure there are enough columns
                    x = float(columns[2].strip()) * 1000 # It multiplies them with 1000 because converting them to meters
                    y = float(columns[3].strip()) * 1000
                    z = float(columns[4].strip()) * 1000
                    horizons_coordinates.append((x, y, z)) # It add the (x,y,z) tuples to list

    with open(input_file, 'r') as file: # It opens your data file with read mode
        input_lines = file.readlines()

    for line in input_lines:
        if line.strip():  # Skip empty lines
            columns = line.split() # Separate them with space
            if len(columns) > 2:  # Ensure there are enough columns
                x, y, z = float(columns[0]), float(columns[1]), float(columns[2])
                input_coordinates.append((x, y, z))

    # If the entry count of your files and API files doesnt match it raises and error make sure your dates are correct.
    if len(horizons_coordinates) != len(input_coordinates):
        raise ValueError("The number of entries in Horizons data and your data do not match")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory) 
    
    with open(output_file, 'w') as file: # It creates the results file for differences and radius calcultaion in write mode.
        file.write("X_diff\tY_diff\tZ_diff\tR_diff\n") # It writes the headings.
        
        differences = [] # It is for difference and radius calculations result tuples. It will be used for plotting.
        for hc, lc in zip(horizons_coordinates, input_coordinates):
            x_diff = hc[0] - lc[0]
            y_diff = hc[1] - lc[1]
            z_diff = hc[2] - lc[2]
            r_diff = math.sqrt((x_diff*x_diff)+(y_diff*y_diff)+(z_diff*z_diff)) # It calculates radius with x,y and z coordinates.
            file.write(f"{x_diff}\t{y_diff}\t{z_diff}\t{r_diff}\n") # It writes the results line by line.
            differences.append((x_diff, y_diff, z_diff,r_diff))

    print(f"Differences saved to {output_file}")

    fig, axs = plt.subplots(4, 1, figsize=(10, 12)) # We will draw plots for each dimension.

    time_points = range(len(differences))
    x_label = 'Days'
    formatter = ticker.FuncFormatter(scientific_format)


    axs[0].plot(time_points, [diff[0] for diff in differences], label='X difference')
    axs[0].set_xlabel(x_label)
    axs[0].set_ylabel('X Difference (m)')
    axs[0].xaxis.set_major_formatter(formatter)
    axs[0].yaxis.set_major_formatter(formatter)
    axs[0].legend()

    axs[1].plot(time_points, [diff[1] for diff in differences], label='Y difference')
    axs[1].set_xlabel(x_label)
    axs[1].set_ylabel('Y Difference (m)')
    axs[1].xaxis.set_major_formatter(formatter)
    axs[1].yaxis.set_major_formatter(formatter)
    axs[1].legend()

    axs[2].plot(time_points, [diff[2] for diff in differences], label='Z difference')
    axs[2].set_xlabel(x_label)
    axs[2].set_ylabel('Z Difference (m)')
    axs[2].xaxis.set_major_formatter(formatter)
    axs[2].yaxis.set_major_formatter(formatter)
    axs[2].legend()

    axs[3].plot(time_points, [diff[3] for diff in differences], label='R difference')
    axs[3].set_xlabel(x_label)
    axs[3].set_ylabel('R Difference (m)')
    axs[3].xaxis.set_major_formatter(formatter)
    axs[3].yaxis.set_major_formatter(formatter)
    axs[3].legend()

    plt.tight_layout()    
    
    fig.savefig(output_plot)

    plt.close(fig)

# Function to convert axis values to scientific format and show with superscripts like x^a
def scientific_format(x, pos):
    if x == 0:
        return "0"
    exponent = int(np.floor(np.log10(abs(x))))
    coeff = x / 10**exponent
    return r"${:.1f} \times 10^{{{}}}$".format(coeff, exponent)

# Function to plot the graph from a data file provided by you. It is used for whole system energy and angular momentum graphs.
def plot_from_file(input_file_name, output_file_name,x_column_index,y_column_index,x_label,y_label):

    values = []

    if not os.path.isfile(input_file_name):
        print(f"Error: File {input_file_name} does not exist.")
        return
    
    with open(input_file_name, "r") as file:
        input_lines =  file.readlines()
    
    for line in input_lines:
        if line.strip():
            columns = line.split()
            if(len(columns) > 1):
                try:
                    x = float(columns[x_column_index])
                    y = float(columns[y_column_index])
                    values.append((x, y))
                except ValueError:
                    print(f"Warning: Non-numeric data found in line: {line.strip()}")
    
    if not values:
        print("No data to plot.")
        return
    
    fig, axs = plt.subplots(figsize=(10,6))
    formatter = ticker.FuncFormatter(scientific_format)

    axs.plot([axis_values[0] for axis_values in values],[axis_values[1] for axis_values in values])
    axs.set(xlabel = x_label, ylabel = y_label)

    axs.xaxis.set_major_formatter(formatter)
    axs.yaxis.set_major_formatter(formatter)
    axs.grid()

    fig.savefig(output_file_name)
    plt.show()



# yyyy-mm-dd
start_time = '2024-02-09' 
stop_time = '2025-02-07'

#7 February 2025 it is the one year end_date
#5 February 2034 it is the ten years end_date
#15 January 2124 it is hundred years end_date
#11 June 3023 it is one thousand years end_date

# Ten major bodies of solar system and id's for their barycenter.
major_bodies = {"1":"Mercury",
                "2":"Venus",
                "3":"Earth-Moon",
                "4":"Mars",
                "5":"Jupiter",
                "6":"Saturn",
                "7":"Uranus",
                "8":"Neptune",
                "9":"Pluto",
                "10":"Sun"} 

# Main function for the run whole functions.
def process_major_body(id,name): 
    output_filename = f"HorizonsResults{name}"
    fetch_ephemerides(id,start_time,stop_time,output_filename) # It takes the ephemerides data from JPL Horizon API
    calc_ephemerides_diff(output_filename, f"{name}Position", f"{name}B") # It calculates difference between JPL data and your calculations results.

for id,name in major_bodies.items():
    process_major_body(id,name)

# Arguments : Name of your data file, Name of output file, X axis column index, Y Axis column index, X axis label, Y axis label )
plot_from_file("WholeSystemEnergy.dat", "WholeSystemEnergy100y1080s", 0,1,"Time (s)", "energy difference")
