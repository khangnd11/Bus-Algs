import pandas as pd
import numpy as np
from tqdm import tqdm

import ast

from tabulate import tabulate

os_path = '/users/ndkhang/Documents/HCMC_Bus'

def main():
    # station_link = pd.read_csv(f"{os_path}/HCMC_Bus/Bus-Algs/data/station_link.csv")
    station_node = pd.read_csv(f"{os_path}/Bus-Algs/data/station_node.csv")
    num_nodes = len(station_node) # number of stations
    
    P_1_matrix = np.load(f"{os_path}/matrix/P_Path/P_1.npy")
    
    # list_nodes = list(station_node.StopId)
    P_2_matrix = np.zeros((num_nodes, num_nodes), dtype=int)
    SW_1_matrix = np.empty((num_nodes, num_nodes), dtype=object)

    for node_i in range(num_nodes):
        for node_j in range(num_nodes):
            if P_1_matrix[node_i][node_j] == 0:
                SW_1_matrix[node_i][node_j] = list()
                
    for node_i in tqdm(range(num_nodes)):
        for node_j in range(num_nodes):
            if (node_i == node_j) or (P_1_matrix[node_i][node_j] == 1) :
                continue
            else:
                for sw in range(num_nodes):
                    if (P_1_matrix[node_i][sw] == 1) and (P_1_matrix[sw][node_j] == 1):
                            P_2_matrix[node_i][node_j] = 1
                            SW_1_matrix[node_i][node_j].append(sw)
                            
    SW_1 = list()
    np.save(f"{os_path}/matrix/P_Path/P_2.npy", P_2_matrix)
    print(P_2_matrix)
    
    for node_i in tqdm(range(num_nodes)):
        for node_j in range(num_nodes):
            if P_2_matrix[node_i][node_j] == 1:
                sw_stops = SW_1_matrix[node_i][node_j]
                SW_1.append([node_i, node_j, sw_stops])

    SW_1_df = pd.DataFrame(SW_1, columns=['Node_i', 'Node_j', 'SwitchStation'])
    SW_1_df.to_csv(f"{os_path}/matrix/P_Path/SW_1.csv", index=False)
    print(tabulate(SW_1_df, headers = 'keys', tablefmt = 'psql'))

if __name__ == '__main__':
    main()