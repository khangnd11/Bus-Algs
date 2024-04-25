import numpy as np
import pandas as pd

from datetime import time, date

from alg import Bus_TravelTime

import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

def get_historical_trajactory(routeNo, dir, day_of_week):
    his_traj = pd.read_csv(f"../data/dummy_data/{routeNo}_{dir}.csv")
    his_traj = his_traj[his_traj.DayOfWeek == day_of_week]
    his_traj.drop(columns=['Date', 'DayOfWeek'], axis=1, inplace=True)
    
    return his_traj

def list_segmentId(trajs):
    id = trajs.iloc[0]['TripId']
    trip = trajs[trajs.TripId == id]
    list_segId = list(trip.SegmentId)
    return list_segId

def travel_time_prediction(routeNo, dir, departure_date, departure_time, v_temp, v_pass, O_station, D_station):
    print(f"Bus RouteNo: {routeNo}")
    day_of_week = departure_date.weekday()
    start_time = departure_time.hour * 3600 + departure_time.minute * 60 + departure_time.second
        
    his_trajs = get_historical_trajactory(routeNo, dir, day_of_week)
    all_segmentId = list_segmentId(his_trajs)
    if (O_station not in all_segmentId) or (D_station not in all_segmentId):
        print("No Station Information Available!")
    else:
        print(f"Departure Date: {departure_date} at {departure_time}")
        print("---------------------------------------------------")
        
        day_of_week = departure_date.weekday()
        start_time = departure_time.hour * 3600 + departure_time.minute * 60 + departure_time.second
        
        print("Historical Trips: ")
        # print(his_trajs)
        print(his_trajs.info())
        print("---------------------------------------------------")
        
        bus_traveltime = Bus_TravelTime(MNT=10,
                                        MNC=5,
                                        Vthresh_temp=v_temp,
                                        Vthresh_pass=v_pass,
                                        historical_trajectory=his_trajs)
        
        print(f"Future Prediction Result - from [{O_station}] to [{D_station}]")   
        
        total_durations = bus_traveltime.future_prediction(departure_time=start_time,
                                        seg_start=O_station,
                                        seg_end=D_station)
        
        print(f"Total durations: {total_durations}s ~~ {total_durations/60}m")
    

def main():
    print("Starting ...")
    
    vthresh_temp = 100000
    vthresh_pass = 1000
    routeNo = 50
    departure_time =  time(7,0,0)  # hh:mm:ss
    departure_date = date(2024, 3, 2) # yyyy-mm-dd
    
    res = travel_time_prediction(routeNo = routeNo,
                                 dir = 1,
                                 departure_date = departure_date,
                                 departure_time = departure_time,
                                 v_temp = vthresh_temp,
                                 v_pass = vthresh_pass,
                                 O_station=7773,
                                 D_station=3385)
    print("Done.")

if __name__ == '__main__':
    main()