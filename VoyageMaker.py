import csv
import math

# Initialize lists
ports_list = []
original_tracking_list = []
voyages = [["vessel", "begin_date", "end_date", "begin_port_id", "end_port_id"]]

# Open the files we will be reading for port and vessal data
# Populate data into lists we will use
with open("ports.csv", encoding="utf8") as ports_file:
    csvreader = csv.reader(ports_file, delimiter=",")
    for row in csvreader:
        ports_list.append(row)
del ports_list[0]

with open("tracking.csv", encoding="utf8") as tracking_file:
    csvreader = csv.reader(tracking_file, delimiter=",")
    for row in csvreader:
        original_tracking_list.append(row)
del original_tracking_list[0] #Delete header

# Goes through ea row of tracking list and compares the Lat/Long of ship to a list of possible ports
# Adds port location to a new tracking list that we will use. 
iterator = 0
for row in original_tracking_list:
    iterator += 1
    for port in ports_list:
        # Precise measurement determines nearby port - can't use just stopped position as a marker
        # as vessal will often be moving slowly about a port or near a port when its essentially entered
        # and sometimes data will show a v low speed but lat/long remain unchanged (errors in speed data).
        if row[5] != "NULL": # Disregard entries where speed is NULL
            if float(row[5]) < 1: # Only consider entries where speed is slow.
                if math.isclose(float(row[2]),float(port[1]),abs_tol=0.12):
                    if math.isclose(float(row[3]),float(port[2]),abs_tol=0.12):
                        row.append(port[0])  # Adds port number to entry

    # Imprecise measurement only utilized if vehicle is in a stopped position
    # So we don't lose potential trips at large ports due to precision of above captures.
    if len(row) != 8:
        if row[5] == "0":
            closest_port = 0
            closeness = 10000
            for port in ports_list:
                # Imprecise measurement determines nearby port
                # So we find when vessels are moored at periphery of a large port
                if math.isclose(float(row[2]), float(port[1]), abs_tol=0.5):
                    if math.isclose(float(row[3]), float(port[2]), abs_tol=0.5):
                        curr_closeness = abs(float(row[2]) - float(port[1])) + abs(float(row[3]) - float(port[2]))
                        if curr_closeness < closeness:
                            closeness = curr_closeness
                            closest_port = port[0]
            if closest_port != 0:
                row.append(closest_port)  # Adds port number to entry if a nearby port was found

# Create new tracking list scrubbing movement data
# Only retains tracking lines sufficiently near a port
tracking_list = []
for ea in original_tracking_list:
    if len(ea) > 7:
        tracking_list.append(ea)

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
    if departures[i][0] == arrivals[i+1][0]:
        voyages.append([departures[i][0],departures[i][1],arrivals[i+1][1],departures[i][7],arrivals[i+1][7]])
    i += 1

# Store Voyages to csv
with open('voyages.csv', 'w', newline='') as voyagesfile:
    v_writer = csv.writer(voyagesfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for ea in voyages:
        v_writer.writerow(ea)

