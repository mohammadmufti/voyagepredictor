import pandas as pd
import csv
import warnings
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics.pairwise import haversine_distances
from math import radians
warnings.simplefilter(action='ignore', category=FutureWarning)

#Initialize global variables
distanceToleranceToKnown = 250 # Tolerance to possibly use a previously touched port (in km)
distanceToleranceToUnknown = 50 # Tolerance to possibly use an untouched port for prediction (in km)

# Open files
voyages = pd.read_csv('voyages.csv', parse_dates=["begin_date","end_date"])
lastcoords = pd.read_csv('lastcoords.csv', index_col='vessel')
ports_list = []
with open('ports.csv', encoding="utf8") as pfile:
    csvreader = csv.reader(pfile, delimiter=",")
    for row in csvreader:
        ports_list.append(row)
del ports_list[0]

# Create a data frame for subsets of timestamp to train model
# to consider seasonality to some extent
mod_voyages = pd.concat([voyages.drop(columns=["begin_date", "end_date", "end_port_id"])], axis=1)
# mod_voyages["Trip_id"] = mod_voyages.groupby("vessel").cumcount()+1 # Index prior trips
mod_voyages['Seasons'] = [d.quarter for d in voyages['end_date']] # Add column for season/quarter
vessels = pd.unique(voyages['vessel'])  # Find unique vessals
predictions = [['vessel', 'begin_port_id', 'end_port_id', 'voyage']]  # Initialize Storage for predictions
model = DecisionTreeClassifier() # Declare ML model

# A function that takes vessel # as an argument, returns closest port within distanceTolerance if it exists.
# Returns 0 if no closest port within restraints
def firstTripFunction(vessel):
    closest_port = 0
    closeness = distanceToleranceToKnown
    # Find relevent ports only:
    vesselports = pd.unique(voyages['end_port_id'].where(voyages.vessel == vessel).dropna())
    for port in ports_list:
        port_latlong = [radians(float(port[1])), radians(float(port[2]))]
        vessel_latlong = [radians(float(lastcoords.at[vessel, 'lat'])), radians(float(lastcoords.at[vessel, 'long']))]
        curr_closeness = haversine_distances([vessel_latlong, port_latlong]) * 6371
        # if (vessel == 8):
        #     print("FOR VESSEL 8 and Port " + str(port[0]) + str(port_latlong) + " "
        #           + str(lastcoords.at[vessel, 'lat']) +
        #           " " + str(lastcoords.at[vessel, 'long']) +
        #             str(curr_closeness[0][1]))
        if int(port[0]) in vesselports.astype(int).tolist():
            if curr_closeness[0][1] < closeness:
                closeness = curr_closeness[0][1]
                closest_port = port[0]
        elif curr_closeness[0][1] < distanceToleranceToUnknown and curr_closeness[0][1] < closeness:
            # print("Using unknown due to extreme proximity")
            # print(str(vessel) + " v:" + str(vessel_latlong) + " p:" + str(port_latlong) + " c:" + str(curr_closeness[0][1])
            #       + '\n port:' + str(port[0]))
            closeness = curr_closeness[0][1]
            closest_port = port[0]
    return int(closest_port)



# Create a list of prediction values using our ML model
for vessel in vessels:
    voyage = 1  # Initialize iterator for predictions
    X = mod_voyages.where(voyages.vessel == vessel).dropna()
    y = voyages["end_port_id"].where(voyages.vessel == vessel).dropna()
    model.fit(X,y)
    # INSERT HERE ALTERNATIVE CODE TO FIND THE FIRST NEW DESTINATION
    begin_port = voyages.loc[voyages.where(voyages.vessel == vessel).last_valid_index(), 'end_port_id']
    end_port = model.predict([[vessel, begin_port,
                               #voyage,
                               4]]) #Predictor fed w vessel, start, trip number and expected season
    initial_trip = firstTripFunction(vessel)
    if initial_trip != 0 and initial_trip != begin_port:
        end_port[0] = initial_trip
        # print("Using proximity idea instead of ML model for " +
        #       str(vessel) + " " +
        #       str(begin_port) + " " +
        #       str(int(end_port[0])) + " " + str(voyage))
    while begin_port == end_port: # If begin port is equal to the end port - rerun model
        print("Re-running" + str(vessel))
        end_port = model.predict([[vessel, begin_port,
                                   # voyage,
                                   1]])  # Predictor fed w vessel, start, trip number and expected season
    predictions.append([vessel, begin_port, int(end_port[0]), voyage])
    # print("First prediction" + str(vessel) + str(begin_port) + str(int(end_port[0])) + str(voyage))
    while (voyage != 3):
        begin_port = int(end_port[0])
        voyage += 1
        end_port = model.predict([[vessel, begin_port,
                                   #voyage,
                                   1]])
        if begin_port == end_port:  # If begin port is equal to the end port - rerun model
            print("Re-running" + str(vessel))
            end_port = model.predict([[vessel, begin_port,
                                       # voyage,
                                       2]])  # Predictor fed w vessel, start, trip number and expected season
        if begin_port == end_port:  # If begin port is equal to the end port - rerun model
            print("Re-running" + str(vessel))
            end_port = model.predict([[vessel, begin_port,
                                       # voyage,
                                       3]])  # Predictor fed w vessel, start, trip number and expected season
        if begin_port == end_port:  # If begin port is equal to the end port - rerun model
            print("Re-running" + str(vessel))
            end_port = model.predict([[vessel, begin_port,
                                       # voyage,
                                       4]])  # Predictor fed w vessel, start, trip number and expected season
        predictions.append([vessel, begin_port, int(end_port[0]), voyage])

# Store Predictions to csv
with open('predict.csv', 'w', newline='') as predictfile:
    p_writer = csv.writer(predictfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for ea in predictions:
        p_writer.writerow(ea)