import pandas as pd
import numpy as np
import csv
import joblib

from sklearn.tree import DecisionTreeClassifier
from sklearn import tree

voyages = pd.read_csv('voyages.csv', parse_dates=["begin_date","end_date"])
model = joblib.load('Voyage_Predictor.joblib')

vessels = pd.unique(voyages['vessel'])  # Find unique vessals
predictions = [['vessel', 'begin_port_id', 'end_port_id', 'voyage']]  # Initialize Storage for predictions

# Create a list of prediction values using our ML model
for vessel in vessels:
    voyage = 1  # Initialize iterator for predictions
    begin_port = voyages.loc[voyages.where(voyages.vessel == vessel).last_valid_index(), 'end_port_id']
    end_port = model.predict([[vessel, begin_port]])
    predictions.append([vessel, begin_port, end_port[0], voyage])
    while (voyage != 3):
        begin_port = end_port[0]
        voyage += 1
        end_port = model.predict([[vessel, begin_port]])
        predictions.append([vessel, begin_port, end_port[0], voyage])

# Store Predictions to csv
with open('predict.csv', 'w', newline='') as predictfile:
    p_writer = csv.writer(predictfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for ea in predictions:
        p_writer.writerow(ea)