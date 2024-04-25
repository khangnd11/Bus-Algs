import pandas as pd
from tqdm import tqdm

from bfs_alg import BFS_Path_Search

        
def bus_path_finding(O_hub, D_hub):
    hub_data_path = "/Users/nguyenduykhang/Documents/Projects/HPCC-BusAlgos/data/bus-lines"
    all_routes = pd.read_csv("/Users/nguyenduykhang/Documents/Projects/HPCC-BusAlgos/data/all_routes.csv")
    num_routes = len(all_routes)
    bus_routes_dict = dict()
    
    for route in tqdm(range(num_routes)):
        routeNo = all_routes.iloc[route]['RouteNo']
        for dir in [0, 1]:
            routeName = f"{routeNo}_{dir}"
            bus_hub = pd.read_csv(f"{hub_data_path}/{routeNo}/{dir}_hub_nodes.csv")
            hub_list = list(bus_hub.StopId)
            bus_routes_dict[routeName] = hub_list
            
    print(f"From [{O_hub}] - To [{D_hub}]")
    path_finder = BFS_Path_Search(routes_dict=bus_routes_dict)
    path_finder.route_graph()
    routes, path = path_finder.path_finding(O_hub=O_hub, D_hub=D_hub)
    
    print(f"Number of Bus Routes: {routes}")
    if routes != -1 and routes != -2:
        switch_hub = path_finder.switch_hub(path)
        print(f"Bus Routes Should Take: {path}")
        print(f"Switching Bus Hub: {switch_hub}")
    
    # print("==========================================")
    # all_path = path_finder.all_path_finding(O_hub=O_hub, D_hub=D_hub)
    # print(all_path)


def main():
    print("Staring...")
    # 3157,BX33,Đại học Bách Khoa
    # 898,Q10 058,Đại học Bách Khoa (cổng sau)
    # 7564,Q1 196,Bảo tàng Mỹ Thuật
    bus_path_finding(O_hub=3157, D_hub=7564)

if __name__ == '__main__':
    main()
    
    