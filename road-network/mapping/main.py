import pandas as pd
import time
from matching import Matching
from interpolation import Kinematic
from tqdm import tqdm
import matplotlib.pyplot as plt
from utils import haversine_distance

# comp.to_csv('/Users/nguyenduykhang/Documents/HPC Lab/Travel Time Prediction/Bus-Travel-Time-Prediction/data/bus50.csv', index=False)


def run_all_tests():
    links = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/50/rev_links.csv')
    nodes = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/50/rev_nodes.csv')
    matching = Matching(nodes, links)
    interpolation = Kinematic(nodes, links)
    
    comp = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/base/comp.csv')
    num_traj = len(comp) - 1
        
    
    print(f"TIME EXECUTE ========================================")
    
    for rate in tqdm(range(1,2)):
        traj= pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/re_traj_50/2805/miss_'+str(rate*10)+'.csv')
    
        start_execute = time.perf_counter()
        traj = matching.candidate_preparation(traj)
        traj = matching.direction_analysis(traj)
        end_execute = time.perf_counter()
        
        print(f"missing rates -- {rate*10}%")
        print(f"MAP MATCHING: {end_execute - start_execute}")
        print("========")
        print(" ====== ")
        print("  ==== ")
        print("   == ")
        
        start_execute = time.perf_counter()
        traj = interpolation.kinematic(traj)
        end_execute = time.perf_counter()
        
        print(f"INTERPOLATIOM: {end_execute - start_execute}")
        print("========")
        print(" ====== ")
        print("  ==== ")
        print("   == ")
        
def diff_diss(comp, traj):
    for inx in range(len(comp)-1):
        org_dist = haversine_distance(comp.loc[inx, 'latitude'],
                                      comp.loc[inx, 'longitude'],
                                      comp.loc[inx+1, 'latitude'],
                                      comp.loc[inx+1, 'longitude'])
        
        comp_dist = haversine_distance(comp.loc[inx, 'imp_latitude'],
                                       comp.loc[inx, 'imp_longitude'],
                                       comp.loc[inx+1, 'imp_latitude'],
                                       comp.loc[inx+1, 'imp_longitude'])
        traj_dist = haversine_distance(traj.loc[inx, 'imp_latitude'],
                                       traj.loc[inx, 'imp_longitude'],
                                       traj.loc[inx+1, 'imp_latitude'],
                                       traj.loc[inx+1, 'imp_longitude'])
        print(f"{inx} --> {inx+1} == {org_dist} -- {comp_dist} -- {traj_dist}")
        
def main():
    comp = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/re_traj_50/2805/miss_00.csv')
    links = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/50/rev_links.csv')
    nodes = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/50/rev_nodes.csv')
    matching = Matching(nodes, links)
    interpolation = Kinematic(nodes, links)
    # traj = pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/re_traj_50/2805/miss_50.csv')
    comp = matching.map_matching(comp)
    comp = interpolation.kinematic(comp)
    
    for rate in tqdm(range(1,6)):
        traj= pd.read_csv('/Users/nguyenduykhang/Documents/HPC Lab/Trajectory-Imputation/data/re_traj_50/2805/miss_'+str(rate*10)+'.csv')
        start_execute = time.perf_counter()
        traj = matching.map_matching(traj)
        traj = interpolation.kinematic(traj)
        end_execute = time.perf_counter()
        print(f"TIME EXECUTE: {end_execute - start_execute}")

        
        
    
    print("========")
    print(" ====== ")
    print("  ==== ")
    print("   == ")
    
    # map_imp()
    
    for inx in range(len(comp)-1):
        org_dist = haversine_distance(comp.loc[inx, 'latitude'],
                                      comp.loc[inx, 'longitude'],
                                      comp.loc[inx+1, 'latitude'],
                                      comp.loc[inx+1, 'longitude'])
        
        comp_dist = haversine_distance(comp.loc[inx, 'imp_latitude'],
                                       comp.loc[inx, 'imp_longitude'],
                                       comp.loc[inx+1, 'imp_latitude'],
                                       comp.loc[inx+1, 'imp_longitude'])
        traj_dist = haversine_distance(traj.loc[inx, 'imp_latitude'],
                                       traj.loc[inx, 'imp_longitude'],
                                       traj.loc[inx+1, 'imp_latitude'],
                                       traj.loc[inx+1, 'imp_longitude'])
        print(f"{inx} --> {inx+1} == {org_dist} -- {comp_dist} -- {traj_dist}")
        
        if traj_dist == 0:
            print(0)
        else:
            print(comp_dist / traj_dist)
    
    
            
if __name__ == '__main__':
    main()