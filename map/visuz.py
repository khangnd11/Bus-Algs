import pandas as pd
from tqdm import tqdm
import folium

from datetime import date

import random

import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

def route_path(routeNo, dir):
    data_path = "/Users/nguyenduykhang/Documents/Projects/HCMC-Bus-Network/data/buyttphcm"
    if dir == 0:
        path = f"{data_path}/{routeNo}/paths_by_var.csv"
    else:
        path = f"{data_path}/{routeNo}/rev_paths_by_var.csv"
    
    path_df = pd.read_csv(path)
    path_df =path_df.join(path_df.shift(-1), rsuffix="_next").dropna()
    return(path_df)

def hub_station(routeNo, dir):
    data_path = "/Users/nguyenduykhang/Documents/Projects/HPCC-BusAlgos/data/bus-lines"
    hub_df = pd.read_csv(f"{data_path}/{routeNo}/{dir}_hub_nodes.csv")
    hub_df.drop(columns=['StopType', 'Zone', 'Ward', 'AddressNo', 'Street', 'SupportDisability', 'Status', 'Search', 'Routes'], axis=1, inplace=True)
    hub_df = hub_df.join(hub_df.shift(-1), rsuffix="_next").dropna()
    hub_df['StopId_next'] = hub_df['StopId_next'].astype(int)
    return hub_df

def map_visualization(routeNo, dir, date, seg_travel_time):
    bus_path = route_path(routeNo=routeNo, dir=dir)
    bus_hub = hub_station(routeNo=routeNo, dir=dir)
    num_hub = len(bus_hub)
    
    avg_location = bus_hub[['Lat', 'Lng']].mean()
    hcmc_map = folium.Map(location=avg_location, zoom_start=13)
    
    for point in bus_path.itertuples():
        marker = folium.CircleMarker(location=(point.lat, point.lng),
                                 radius=5,
                                 color='green',
                                 fill_color='green',
                                 fill=True,
                                 fill_opacity=1)
        line = folium.PolyLine(locations=[(point.lat, point.lng), (point.lat_next, point.lng_next)])
        marker.add_to(hcmc_map)
        line.add_to(hcmc_map)

    for hub in bus_hub.itertuples():
        OD_hub = (hub.Index == 0) or (hub.Index == num_hub)
        # maker for the current hub
        icon = folium.Icon(icon='home' if OD_hub else 'info-sign',
                           color='cadetblue' if OD_hub else 'green')
        
        marker = folium.Marker(location=(hub.Lat, hub.Lng),
                               icon=icon,
                               tooltip=f"<b>StopID</b>: {hub.StopId} <br>" \
                                   + f"<b>Name</b>: {hub.Name} <br>")
        line = folium.PolyLine(locations=[(hub.Lat, hub.Lng), (hub.Lat_next, hub.Lng_next)],
                               color='red',
                               tooltip=f"<b>Date</b>: {date} <br>" \
                               + f"<b>From</b>: {hub.StopId} <br>" \
                                   + f"<b>To</b>: {hub.StopId_next} <br>" \
                                       + f"<b>Travel Time</b>: {seg_travel_time[hub.Index]} s")
        marker.add_to(hcmc_map)
        line.add_to(hcmc_map)

    folium.Marker(location=(hub.Lat_next, hub.Lng_next),
                  icon=folium.Icon(icon='home', color='cadetblue'),
                  tooltip=f"<b>StopID</b>: {hub.StopId_next} <br>" \
                      + f"<b>Name</b>: {hub.Name_next} <br>").add_to(hcmc_map)
    
    print(hcmc_map)
    hcmc_map.save("map.html")
    
def main():
    print("Starting....")
    departture_date = date(2024, 3, 2)
    seg_travel_time = [random.randint(1, 100) for _ in range(100)]
    map_visualization(routeNo=50, dir=0, date=departture_date, seg_travel_time=seg_travel_time)
    print("Done.")


if __name__ == '__main__':
    main()
    
