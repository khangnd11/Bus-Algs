import pandas as pd
import numpy as np
from tqdm import tqdm
from tabulate import tabulate

os_path = '/users/ndkhang/Documents/HCMC_Bus'

def main():
    # station_link = pd.read_csv(f"{os_path}/HCMC_Bus/Bus-Algs/data/station_link.csv")
    station_node = pd.read_csv(f"{os_path}/HCMC_Bus/Bus-Algs/data/station_node.csv")
    num_nodes = len(station_node) # number of stations
    
    P_1_matrix = np.load(f"{os_path}/matrix/P_Path/P_1.npy")
    P_2_matrix = np.load(f"{os_path}/matrix/P_Path/P_2.npy")
    
    P_3_matrix = np.zeros((num_nodes, num_nodes), dtype=int)
    SW_2_1_matrix = np.empty((num_nodes, num_nodes), dtype=object)
    SW_2_2_matrix = np.empty((num_nodes, num_nodes), dtype=object)

    for node_i in tqdm(range(num_nodes)):
        for node_j in range(num_nodes):
            if (node_i == node_j) or (P_1_matrix[node_i][node_j] == 1) or (P_2_matrix[node_i][node_j] == 1):
                continue
            else:
                for sw in range(num_nodes):
                    if (P_1_matrix[node_i][sw] == 1) and (P_1_matrix[sw][node_j] == 1):
                            P_2_matrix[node_i][node_j] = 1
                            SW_1_matrix[node_i][node_j].append(sw)
                            
    SW_1 = list()
    
    for node_i in tqdm(range(num_nodes)):
        for node_j in range(num_nodes):
            if P_3_matrix[node_i][node_j] == 1:
                sw_21_stops = SW_2_1_matrix[node_i][node_j]
                SW_2_1.append([node_i, node_j, sw_21_stops])
                sw_22_stops = SW_2_2_matrix[node_i][node_j]
                SW_2_2.append([node_i, node_j, sw_22_stops])

    SW_21_df = pd.DataFrame(SW_2_1, columns=['Node_i', 'Node_j', 'SwitchStation'])
    SW_21_df.to_csv(f"{os_path}/algorithms/ver_1/matrix/B_BusRoute/SW_21.csv", index=False)

    SW_22_df = pd.DataFrame(SW_2_2, columns=['Node_i', 'Node_j', 'SwitchStation'])
    SW_22_df.to_csv(f"{os_path}/algorithms/ver_1/matrix/B_BusRoute/SW_21.csv", index=False)
    print(P_3_matrix)

if __name__ == '__main__':
    main()