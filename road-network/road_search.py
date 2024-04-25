import pandas as pd
from tqdm import tqdm

from mapping.mapping import Road_Mapping

import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)


def bus_stop_geometry(all_bus_stops, hcmc_road_geometry):
    geometry = pd.read_csv(hcmc_road_geometry)
    geometry.loc[:, 'nodeID'] = range(len(geometry))
    
    bus_stops = pd.read_csv(all_bus_stops)
    num_bus_stop = bus_stops.stopID.nunique()
    
    in_road = []
    
    road_mapping = Road_Mapping(geometry, sigma=5, error_radius=50)
    for stop in tqdm(range(num_bus_stop)):
        stop_lng = bus_stops.iloc[stop]['lng']
        stop_lat = bus_stops.iloc[stop]['lat']
        stopID = bus_stops.iloc[stop]['stopID']
        
        poss_road_id = road_mapping.candidate_road([stop_lng, stop_lat])
        in_road.append([stopID, poss_road_id])
        print(poss_road_id)
        
    stop_in_road = pd.DataFrame(in_road, columns=['stopID', 'poss_road_id'])
    stop_in_road.to_csv('../data/bus_stop_in_road_50.csv', index=False)


def process_path(routeNo, path_df, road_mapping, road_infor, dir_flag):
    path_data = []
    for index, row in path_df.iterrows():
        point_lng, point_lat = row['lng'], row['lat']
        poss_road_id, ver_lng, ver_lat, other_poss_road = road_mapping.candidate_road([point_lng, point_lat])
        poss_road = road_infor[road_infor.id == poss_road_id]
        if not poss_road.empty:
            road_name, road_district = poss_road.iloc[0]['tenduong'], poss_road.iloc[0]['tenquan']
            path_data.append([routeNo, dir_flag, poss_road_id, point_lng, point_lat, ver_lng, ver_lat, road_name, road_district, other_poss_road])
    return path_data

def bus_path_geometry(hcmc_road_infor, hcmc_road_geometry, all_bus_route, sigma, error_radius, bus_route):
    print("Starting ...")
    
    try:
        road_infor = pd.read_csv(hcmc_road_infor)
        geometry = pd.read_csv(hcmc_road_geometry)
        geometry['nodeID'] = range(len(geometry))

        road_mapping = Road_Mapping(geometry, sigma, error_radius)
        
        print("Processing Route: ... ", bus_route)
        for dir_flag in [0, 1]:
            path_file = f'../data/buyttphcm/{bus_route}/{["paths_by_var", "rev_paths_by_var"][dir_flag]}.csv'
            path_df = pd.read_csv(path_file)
            path_geo = process_path(bus_route, path_df, road_mapping, road_infor, dir_flag)
            
            path_geo_df = pd.DataFrame(path_geo, columns=['routeNo', 'dir', 'poss_road_id', 'point_lng', 'point_lat', 'ver_lng', 'ver_lat', 'tenduong', 'tenquan', 'other_poss_road'])
            path_geo_df.to_csv(f"../data/{bus_route}_{dir_flag}_path_geometry.csv", index=False)
        print("Done.")
        
        # for route in tqdm(bus_route, desc="Processing Routes"):
        #     print(f"RouteNO: {route} ...")
        #     for dir_flag in [0, 1]:
        #         path_file = f'../data/buyttphcm/{route}/{["paths_by_var", "rev_paths_by_var"][dir_flag]}.csv'
        #         path_df = pd.read_csv(path_file)
        #         all_paths += process_path(route, path_df, road_mapping, road_infor, dir_flag)

        # all_bus_path = pd.DataFrame(all_paths, columns=['routeNo', 'dir', 'poss_road_id', 'point_lng', 'point_lat', 'ver_lng', 'ver_lat', 'tenduong', 'tenquan', 'other_poss_road'])
        # all_bus_path.to_csv('../data/bus_path_50.csv', index=False)
        # print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    hcmc_road_infor = './hcmc_road_infor.csv'
    hcmc_road_geometry = './road_geometry.csv'
    # all_bus_stops = '../data/all_bus_stops.csv'
    all_bus_route = '../data/route_information.csv'
    
    bus_route = 50
    sigma = 2
    error_radius = 10
    bus_path_geometry(hcmc_road_infor, hcmc_road_geometry, all_bus_route, sigma, error_radius, bus_route)

if __name__ == '__main__':
    main()