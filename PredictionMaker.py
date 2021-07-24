import pandas as pd
import csv
import joblib
import numpy as np

from sklearn.tree import DecisionTreeClassifier

voyages = pd.read_csv('voyages.csv', parse_dates=["begin_date","end_date"])

# Create a data frame for subsets of timestamp to train model
# to consider seasonality to some extent
mod_voyages = pd.concat([voyages.drop(columns=["begin_date", "end_date", "end_port_id"])], axis=1)
mod_voyages["Trip_id"] = mod_voyages.groupby("vessel").cumcount()+1 # Index prior trips
mod_voyages['Seasons'] = [d.quarter for d in voyages['begin_date']] # Add column for season/quarter
vessels = pd.unique(voyages['vessel'])  # Find unique vessals
predictions = [['vessel', 'begin_port_id', 'end_port_id', 'voyage']]  # Initialize Storage for predictions
model = DecisionTreeClassifier() # Declare ML model

# Create a list of prediction values using our ML model
for vessel in vessels:
    voyage = 1  # Initialize iterator for predictions
    X = mod_voyages.where(voyages.vessel == vessel).dropna()
    y = voyages["end_port_id"].where(voyages.vessel == vessel).dropna()
    model.fit(X,y)
    # INSERT HERE ALTERNATIVE CODE TO FIND THE FIRST NEW DESTINATION
    begin_port = voyages.loc[voyages.where(voyages.vessel == vessel).last_valid_index(), 'end_port_id']
    end_port = model.predict([[vessel, begin_port, voyage,1]]) #Predictor fed w vessel, start, trip number and expected season
    predictions.append([vessel, begin_port, end_port[0], voyage])
    while (voyage != 3):
        begin_port = end_port[0]
        voyage += 1
        end_port = model.predict([[vessel, begin_port, voyage, 1]])
        predictions.append([vessel, begin_port, end_port[0], voyage])

# Store Predictions to csv
with open('predict.csv', 'w', newline='') as predictfile:
    p_writer = csv.writer(predictfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for ea in predictions:
        p_writer.writerow(ea)