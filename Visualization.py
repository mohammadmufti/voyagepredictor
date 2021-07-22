import folium
import pandas as pd
import folium.plugins as plugins

tracking = pd.read_csv('Debug\Maps\\tracking.csv')
ports = pd.read_csv('ports.csv')
vessels = pd.unique(tracking['vessel'])  # Find unique vessals
rad = 3000 # Set radius for ports

# Function to start a map w just the ports
def startmap():
    m = folium.Map(
        location=[59.338315,18.089960],
        tiles='cartodbpositron',
        zoom_start=2,
    )
    ports.apply(lambda row:folium.Circle(location=[row["lat"], row["long"]],
                                         tooltip=row['port'],
                                         radius = rad).add_to(m), axis=1)
    return m



for vessel in vessels:
    m = startmap() #Starts a map with ports
    currtracking = tracking.where(tracking.vessel==vessel).dropna()
    currtracking.apply(lambda row:folium.Circle(location=[row["lat"], row["long"]],
                                                 radius = 0.5,
                                                 color = 'red',
                                                 tooltip=str(row['speed'])+' + '+str(row['datetime'])
                                                 ).add_to(m), axis=1)
    lastlat = tracking.loc[tracking.where(tracking.vessel == vessel).last_valid_index(), 'lat']
    lastlong = tracking.loc[tracking.where(tracking.vessel == vessel).last_valid_index(), 'long']
    lastspeed = tracking.loc[tracking.where(tracking.vessel == vessel).last_valid_index(), 'speed']
    lasthead = tracking.loc[tracking.where(tracking.vessel == vessel).last_valid_index(), 'heading']
    lastdraft = tracking.loc[tracking.where(tracking.vessel == vessel).last_valid_index(), 'draft']
    plugins.BoatMarker(location=[lastlat,lastlong],
                       heading = lasthead,
                       popup = str(lastspeed) + " + " + str(lastlat) + " + " + str(lastlong)).add_to(m)
    print("Processing " + str(vessel))
    m.save('Debug\Maps\\WithLastCoords\\'+str(vessel)+'.html')
