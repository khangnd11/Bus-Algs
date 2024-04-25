import multiprocessing as mp
from bus_travel_time import BusPrediction
from utils import *

import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

def worker(vth_temp, vth_pass, his_bus_trajs, bus_trajs, seg_start, seg_end, direction):
    diff_list = []
    MAE_list = []
    RMSE_list = []
    
    bus_prediction = BusPrediction(MNT=5, 
                                   MNC=3, 
                                   Vthresh_temp=vth_temp, 
                                   Vthresh_pass=vth_pass, 
                                   his_bus_trajs=his_bus_trajs)
    
    trip_ids = bus_trajs.trip_id.unique()
    for trip in trip_ids:
        org_traj = bus_trajs[bus_trajs.trip_id == trip] # prediction trip
        
        pre_traj = bus_prediction.future_travel_time(tripID=trip,
                                                    day_of_week=org_traj.iloc[0]['day_of_week'], 
                                                    start_time=org_traj.iloc[0]['start_time'],
                                                    seg_start_time= org_traj.iloc[0]['seg_start_time'],
                                                    seg_start=seg_start,
                                                    seg_end=seg_end)
        
        diff, MAE, RMSE = MAE_RMSE(org_traj, pre_traj)
        diff_list.append(diff/60)
        MAE_list.append(MAE)
        RMSE_list.append(RMSE)
    # print(f"temp: {vth_temp} -- pass: {vth_pass} ===>> {max(diff_list)/60}")  
    # print(f"temp: {vth_temp} -- pass: {vth_pass} ===>> {max(MAE_list)}")  
    # diff_list = [x for x in diff_list if not (pd.isnull(x))]
    # MAE_list = [x for x in MAE_list if not (pd.isnull(x))]
    
    # print(f"temp: {vth_temp} -- pass: {vth_pass} ===>> AVG diff {np.average(diff_list)} -- AVG MAE {np.average(MAE_list)}")  
    nan = [x for x in MAE_list if pd.isnull(x)]
    
    if len(nan) == 0:
        print(f"temp: {vth_temp} -- pass: {vth_pass} ===>> AVG RMSE {np.average(RMSE_list)} -- AVG MAE {np.average(MAE_list)}")  
        plot("Diff", ls=diff_list, vth_temp=vth_temp, vth_pass=vth_pass, direc=direction)
        plot("MAE", ls=MAE_list, vth_temp=vth_temp, vth_pass=vth_pass, direc=direction)
        plot("RMSE", ls=RMSE_list, vth_temp=vth_temp, vth_pass=vth_pass, direc=direction)
    
def in_direction():
    vthresh_temp = [500000,1000000, 2000000, 5000000, 10000000, 20000000, 50000000]
    vthresh_pass = [5000, 10000, 50000, 100000, 1000000, 2000000, 5000000, 10000000]
    
    # Kandy to Digana
    print("--- Kandy to Digana")
    all_bus_trajs = pd.read_csv('./Kandy_to_Digana/kandy_to_digana.csv')
    all_bus_trajs.drop(columns=['date', 'dwell_time', 'hour', 'month'], inplace=True)
    
    # his_bus_trajs = pd.read_csv('./Kandy_to_Digana/his_bus_trajs_1.csv')
    # his_bus_trajs.drop(columns=['date', 'dwell_time', 'hour', 'month'], inplace=True)
    # bus_trajs = pd.read_csv('./Kandy_to_Digana/bus_trajs_1.csv')
    # bus_trajs.drop(columns=['date', 'dwell_time', 'hour', 'month'], inplace=True)
    
    # Create a Pool for parallel processing
    with mp.Pool(mp.cpu_count()) as pool:
        results = []
        for vth_temp in tqdm(vthresh_temp):
            for vth_pass in vthresh_pass:
                # result = pool.apply_async(worker, (vth_temp, vth_pass, his_bus_trajs, bus_trajs, 1, 15, 1))
                result = pool.apply_async(worker, (vth_temp, vth_pass, all_bus_trajs, all_bus_trajs, 1, 15, 1))
                results.append(result)

        pool.close()
        # Wait for all processes to finish
        for result in tqdm(results):
            result.get()
    
    # # Digana to Kandy
    print("--- Digana to Kandy")
    all_bus_trajs = pd.read_csv('./Digana_to_Kandy/digana_to_Kandy.csv')
    all_bus_trajs.drop(columns=['date', 'dwell_time', 'hour', 'month'], inplace=True)
    
    
    with mp.Pool(mp.cpu_count()) as pool:
        results = []
        for vth_temp in tqdm(vthresh_temp):
            for vth_pass in vthresh_pass:
                # result = pool.apply_async(worker, (vth_temp, vth_pass, his_bus_trajs, bus_trajs, 1, 15, 1))
                result = pool.apply_async(worker, (vth_temp, vth_pass, all_bus_trajs, all_bus_trajs, 21, 34, 2))
                results.append(result)

        pool.close()
        # Wait for all processes to finish
        for result in tqdm(results):
            result.get()
        
def main():
    print("Starting up...")
    in_direction()
    print("===========>>>> DONE.")
    
    
if __name__ == '__main__':
    main() 


# def in_small_trajs():
#     vthresh = [1, 10, 100, 500, 1000, 5000, 10000, 50000, 100000]
    
#     # Kandy to Digana
#     all_trajs = pd.read_csv('./1_Kandy_to_Digana.csv')
    
#     all_trajs.drop(columns=['date'], inplace=True)
#     trip_ids = list(all_trajs.trip_id.unique())
    
#     trip = 1
#     org_traj = all_trajs[all_trajs.trip_id == trip] # prediction trip
#     day = org_traj.iloc[0]['day_of_week']
    
#     bus_trajs = all_trajs[(all_trajs.trip_id != trip) & (all_trajs.day_of_week == day)]
#     bus_prediction = BusPrediction(MNT=10, 
#                                    MNC=5,
#                                    Vthresh_temp=100000, 
#                                    Vthresh_pass=100000, 
#                                    bus_trajs=bus_trajs)
    
#     print(f"trip ID: {trip}")
#     print(org_traj)
    
#     pre_traj = bus_prediction.future_travel_time(day_of_week=day, 
#                                                  start_time=org_traj.iloc[0]['start_time'],
#                                                  seg_start_time= org_traj.iloc[0]['seg_start_time'],
#                                                  seg_start=1,
#                                                  seg_end=15)
    
#     diff, MAE, RMSE = MAE_RMSE(org=org_traj, pre=pre_traj)
#     print(pre_traj)
#     print(f"====>> diff: {diff/60} -- MAE: {MAE/60} -- RMSE: {RMSE/60}")
 