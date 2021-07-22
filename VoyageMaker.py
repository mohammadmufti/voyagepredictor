import csv
from math import radians
import pandas as pd
from sklearn.metrics.pairwise import haversine_distances

# Filenames - edit here for debugging as needed
tracking_file = 'tracking.csv'
ports_file = 'ports.csv'
voyages_file = 'voyages.csv'
ports_touched_file = 'tracking_list_ports_touched.csv'
last_coords_file = 'lastcoords.csv'

# Initialize lists
ports_list = []
original_tracking_list = []
voyages = [["vessel", "begin_date", "end_date", "begin_port_id", "end_port_id"]]

# Open the files we will be reading for port and vessal data
# Populate data into lists we will use
# Open the Ports file
with open(ports_file, encoding="utf8") as pfile:
    csvreader = csv.reader(pfile, delimiter=",")
    for row in csvreader:
        ports_list.append(row)
del ports_list[0]

# Open the tracking file
with open(tracking_file, encoding="utf8") as tfile:
    csvreader = csv.reader(tfile, delimiter=",")
    for row in csvreader:
        original_tracking_list.append(row)
del original_tracking_list[0] #Delete header

# Open the tracking file as a DataFrame
original_tracking_pd = pd.read_csv(tracking_file, parse_dates=["datetime"])

# Goes through ea row of tracking list and compares the Lat/Long of ship to a list of possible ports
# Adds port location to a new tracking list that we will use. 
iterator = 0
for row in original_tracking_list:
    print("Processing Tracking Line " + str(iterator) + " of " + str(len(original_tracking_list)))
    iterator += 1
    row_latlong = [radians(float(row[2])),radians(float(row[3]))]
    closest_port = 0
    closeness = 3 # at most 3 km away (largest port I know of has a total berth length of roughly 20 km)
    for port in ports_list:
        # Precise measurement determines nearby port - can't use just stopped position as a marker
        # as vessal will sometimes be moving slowly about a port or near a port when its essentially entered
        # and sometimes data will show a v low speed but lat/long remain unchanged (errors in speed data).
        if row[5] != "NULL": # Disregard entries where speed is NULL
            if float(row[5]) < 0.2: # Only consider entries where speed is very slow or zero.
                port_latlong = [radians(float(port[1])),radians(float(port[2]))]
                curr_closeness = haversine_distances([row_latlong,port_latlong]) * 6371
                if curr_closeness[0][1] < closeness:
                    closeness = curr_closeness[0][1]
                    closest_port = port[0]
    if closest_port != 0:
        row.append(closest_port)

# Create new tracking list scrubbing movement data
# Only retains tracking lines sufficiently near a port
tracking_list = []
index = 0
for ea in original_tracking_list:
    if len(ea) > 7:
        ea.append(index)
        tracking_list.append(ea)
    index += 1

# Create copy of tracking list w only departures
departures = tracking_list.copy()
prev = departures[0]
i = 1
while i < len(departures):
    if departures[i][7] == prev[7]:
        if departures[i][0] == prev[0]:
            departures.pop(i-1)
            prev = departures[i-1]
        else:
            i += 1
            prev = departures[i-1]
    else:
        i += 1
        prev = departures[i - 1]

# Create copy of tracking list w only arrivals.
arrivals = tracking_list.copy()
prev = arrivals[0]
i = 1
while i < len(arrivals):
    if arrivals[i][7] == prev[7]:
        if arrivals[i][0] == prev[0]:
            arrivals.pop(i)
        else:
            i += 1
            prev = arrivals[i-1]
    else:
        i += 1
        prev = arrivals[i - 1]

# Create a list of voyages
i = 0
while (i+1<len(arrivals)):
    # print("Processing voyages line "+ str(i) + " of " + str(len(arrivals)))
    if departures[i][0] == arrivals[i+1][0]:
        a_index = int(arrivals[i+1][8]) - 1 #Index before arriving at current port
        d_index = int(departures[i+1][0]) + 2  #Index exactly upon leaving current port
        voyages.append([original_tracking_list[int(departures[i][8])][0],
                        original_tracking_list[int(departures[i][8])+1][1],
                        original_tracking_list[int(arrivals[i+1][8])][1],
                        original_tracking_list[int(departures[i][8])][7],
                        original_tracking_list[int(arrivals[i+1][8])][7]])
        # voyages.append([departures[i][0],departures[i][1],arrivals[i+1][1],departures[i][7],arrivals[i+1][7]])
    i += 1

# Store Voyages to csv
with open(voyages_file, 'w', newline='') as vfile:
    v_writer = csv.writer(vfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for ea in voyages:
        v_writer.writerow(ea)

# Store tracking list to csv - for debugging and visualization purposes.
with open(ports_touched_file, 'w', newline='') as tlpt:
    tlpt_writer = csv.writer(tlpt, delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
    for ea in tracking_list:
        tlpt_writer.writerow(ea)

# A CSV File which tracks the last known coordinates of a vessel
original_tracking_pd.groupby(['vessel'], as_index=False).last().to_csv(last_coords_file,
                                                                      encoding='utf-8',
                                                                      index=False)