from collections import defaultdict, deque

class BFS_Path_Search:
    def __init__(self, routes_dict):
        self.routes_dict = routes_dict
        self.hubs_dict = defaultdict(set)
        self.adjacency_dict = defaultdict(set)
    
    def route_graph(self):
        print("Building route graph ...")
        for route, hubs in self.routes_dict.items():
            for hub in hubs:
                self.hubs_dict[hub].add(route)
        
        for hubs in self.hubs_dict.values():
            for hub_i in hubs:
                for hub_j in hubs:
                    if hub_i != hub_j:
                        self.adjacency_dict[hub_i].add(hub_j)
    
    def path_finding(self, O_hub, D_hub):
        if O_hub == D_hub:
            return 0, []
        
        O_routes = self.hubs_dict[O_hub]
        D_routes = self.hubs_dict[D_hub]
        
        if not O_routes or not D_routes:
            return -1, []
        
        queue = deque([(route, 1, [route]) for route in O_routes])
        passed = set()
        while queue:
            current_route, dis, route = queue.popleft()
            if current_route in D_routes:
                return dis, route
            passed.add(current_route)
            for neighbor_route in self.adjacency_dict[current_route]:
                if neighbor_route not in passed:
                    queue.append((neighbor_route, dis+1, route+[neighbor_route]))
                    
        return -2, []
    
    def switch_hub(self, travel_path):
        switch_hub = set()
        for route in range(len(travel_path) - 1):
            current_route = travel_path[route]
            next_route = travel_path[route+1]
            switch_hub.update(set(self.routes_dict[next_route]) & set(self.routes_dict[current_route]))
            
        return (switch_hub)
    
    def all_path_finding(self, O_hub, D_hub):
        if O_hub == D_hub:
            return [[O_hub]]
        
        all_paths = list()
        queue = deque([[O_hub]])
        while queue:
            current_path = queue.popleft()
            current_hub = current_path[-1]
            if current_hub == D_hub:
                all_paths.append(current_path)
            for neighbor_hub in self.adjacency_dict[current_hub]:
                if neighbor_hub not in current_path:
                    new_path = current_path + [neighbor_hub]
                    queue.append(new_path)
        
        return all_paths
        
        
        
        