import folium
from folium import plugins
import pandas as pd

ports = pd.read_csv('ports.csv')
locations = pd.read_csv('TrackingVessel1.csv')

m = folium.Map(
    location=[59.338315,18.089960],
    tiles='cartodbpositron',
    zoom_start=2,
)

ports.apply(lambda row:folium.Circle(location=[row["lat"], row["long"]],
                                     tooltip=row['port'],
                                     radius = 1000).add_to(m), axis=1)

locations.apply(lambda row:folium.Circle(location=[row["lat"], row["long"]],
                                         radius = 0.5,
                                         color = 'red',
                                         tooltip=str(row['speed'])+' + '+str(row['datetime'])
                                         ).add_to(m), axis=1)
m.save('map1.html')
