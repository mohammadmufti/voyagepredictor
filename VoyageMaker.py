import csv
from math import radians
import pandas as pd
from sklearn.metrics.pairwise import haversine_distances
import sys

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
initvoyages = []

# Initialize Global Logic variables
zerospeed = 0.5 # What is the upper limit of vessel speed, non-inclusive, at which the vessel is stopped
draftTolerance = 0.1  # Draft must fluctuate more than this number to indicate docking (in meters)
distanceTolerance = 25 # Vessel must be no further than this distance (in km) from a given port.
prearrival = 10 # How far before an arrival do we look to check draft delta
postdeparture = 10 # How far after a departure do we look to check draft delta.

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

# PORT MARKER - MARKS CLOSEST PORT TO LINE ITEM AS APPROPRIATE
# Goes through ea row of tracking list and compares the Lat/Long of ship to a list of possible ports
# Adds port location to a new tracking list that we will use. 
iterator = 0
for row in original_tracking_list:
    print("Processing Tracking Line " + str(iterator) + " of " + str(len(original_tracking_list)))
    iterator += 1
    row_latlong = [radians(float(row[2])),radians(float(row[3]))]
    closest_port = 0
    closeness = distanceTolerance
    for port in ports_list:
        # Precise measurement determines nearby port - can't use just stopped position as a marker
        # as vessal will sometimes be moving slowly about a port or near a port when its essentially entered
        # and sometimes data will show a v low speed but lat/long remain unchanged (errors in speed data).
        if row[5] != "NULL": # Disregard entries where speed is NULL
            if float(row[5]) < zerospeed: # Only consider entries where speed is very slow or zero.
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

# VOYAGE MAKER - CREATE AN INITIAL LIST OF POTENTIAL VOYAGES
i = 0
totalLines = len(arrivals)
while (i+1 < totalLines):
    print("Processing voyages line "+ str(i) + " of " + str(len(arrivals)))
    if departures[i][0] == arrivals[i+1][0]:
        a_index = int(arrivals[i+1][8]) - prearrival #Index x days before arriving at current port (prev a_index = int(arrivals[i+1][8]) - 1)
        d_index = int(departures[i+1][8]) + postdeparture  #Index x days after leaving port (d_index = int(departures[i+1][8]) + 2)
        counter = a_index
        draftdelta = 0
        deltaFirst = "NULL"
        while deltaFirst == "NULL" and counter < d_index:
            deltaFirst = original_tracking_list[counter][6]
            counter += 1
        counter = a_index # Reset the counter
        if deltaFirst == "NULL": # Crash out of code if all drafts in a section are null - debug
            sys.exit("ALL DRAFT VALUES FROM " + str(a_index) + " TO " + str(d_index) + " ARE NULL _ ERROR")
        while counter <= d_index:
            if (original_tracking_list[counter][6] != 'NULL'): # Checks that draft is not NULL
                if original_tracking_list[counter][0] == departures[i][0]: # Checks that line is for current vessel
                    draftvar = abs(float(deltaFirst) - float(original_tracking_list[counter][6]))
                    if draftdelta < draftvar:
                        draftdelta = draftvar
            counter += 1
        initvoyages.append([departures[i][0],departures[i][1],arrivals[i+1][1],departures[i][7],arrivals[i+1][7],draftdelta])
    i += 1

# CREATE A FINALIZED LIST OF VOYAGES
# We will create a new list of voyages, with trips deemed non-trips removed (for lack of change in draft)
# also we truncate the draft delta column data and store only the necessary information.
line = []
for voyage in initvoyages:
    if voyage[5] <= draftTolerance: # For debugging
        print(voyage)
    if voyage[5] >= draftTolerance:
        if line == []: # If line is blank
            voyages.append(voyage[0:5])
        elif voyage[0] == line[0]: # If current vessel is same as prev vessel
            if line[2] != voyage[4]: # If ports are unique
                line.insert(-1,voyage[2])
                line.append(voyage[4])
                voyages.append(line.copy())
                line.clear()
            else:
                # We do not append to final voyages when its a same port to same port trip
                print("Same port to same port trip")
                print(line)
                print(voyage)
        else:
            voyages.append(voyage[0:5])
            line.clear()
    else:
        if line == []:
            line = [voyage[0],
                    voyage[1],
                    voyage[3]]

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