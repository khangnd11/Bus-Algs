from mapping.utils import *

class Road_Mapping:
    def __init__(self, nodes, links, sigma=10, error_radius=10):
        self.sigma = sigma
        self.error_radius = error_radius
        self.nodes_dict = nodes.set_index('NodeId').T.to_dict('list')
        self.links_dict = links.set_index('LinkId').T.to_dict('list')
        self.num_link = list(links.LinkId)
        # self.nodes_dict = {row.nodeID: list(row)[1:] for row in nodes.itertuples()}
    
    def spatial_probability(self, bus_path_point, link):
        start_lng = link[0]
        start_lat = link[1]
        end_lng = link[2]
        end_lat = link[3]
        
        point_lng = bus_path_point[0]
        point_lat = bus_path_point[1]
        
        vertical_projection_lat, vertical_projection_lng = project_gps_point(start_lat,
                                                                             start_lng, 
                                                                             end_lat,
                                                                             end_lng,
                                                                             point_lat,
                                                                             point_lng)
        # within error radius
        disp_3 = haversine_distance(point_lat, point_lng, vertical_projection_lat, vertical_projection_lng)
        # caculate distance
        disp_1 = haversine_distance(point_lat, point_lng, start_lat, start_lng)
        disp_2 = haversine_distance(point_lat, point_lng, end_lat, end_lng)
        
        H = min(disp_1, disp_2, disp_3)
        G_1 = 1 / (sqrt(2 * pi) * self.sigma) * exp(- (H ** 2) / (2 * (self.sigma ** 2)))
        
        return G_1
    
    def comprehensive_probability(self, bus_path, link):
        # return sqrt(self.spatial_probability(trajID, linkID) * self.directional_probability(trajID, linkID, nex_TrajID))
        # return sqrt(self.spatial_probability(trajID, linkID) * self.transmission_probability(pre, trajID, ver_lat, ver_lng, linkID))
        return sqrt(self.spatial_probability(bus_path, link) * 1)
    
    
    def candidate_road(self, bus_path_point):
        point_lng = bus_path_point[0]
        point_lat = bus_path_point[1]
        
        candidate = vertical_projection_lat = vertical_projection_lng = None
        # self.update_node_dict(possible_road_df)
        # G = 0
        G = self.error_radius
        g_dict = dict()
        
        for link in self.num_link:
            Snode = self.links_dict[link][0]
            Enode = self.links_dict[link][1]
            road_id = self.nodes_dict[link][0]
            
            start_lng = self.nodes_dict[Snode][1]
            start_lat = self.nodes_dict[Snode][2]
            end_lng = self.nodes_dict[Enode][1]
            end_lat = self.nodes_dict[Enode][2]
            
            if (start_lat == end_lat) or (start_lng == end_lng):
                continue
            
            vertical_projection_lat, vertical_projection_lng = project_gps_point(start_lat,
                                                                                 start_lng,
                                                                                 end_lat,
                                                                                 end_lng,
                                                                                 point_lat,
                                                                                 point_lng)
            # within error radius
            dist = haversine_distance(point_lat, point_lng, vertical_projection_lat, vertical_projection_lng)
            if dist <= self.error_radius:
                s2e = haversine_distance(start_lat, start_lng, end_lat, end_lng)
                s2v = haversine_distance(start_lat, start_lng, vertical_projection_lat, vertical_projection_lng)
                v2e = haversine_distance(vertical_projection_lat, vertical_projection_lng, end_lat, end_lng)
                if round(abs(s2e - s2v - v2e), 1) == 0.0:
                    # g = sqrt(self.spatial_probability([point_lng, point_lat], [start_lng, start_lat, end_lng, end_lng]) * 1)
                    g = dist
                    if g <= G:
                        G = g
                        candidate = road_id
                    # g = self.comprehensive_probability([point_lng, point_lat], [start_lng, start_lat, end_lng, end_lng])
                    # if g >= G:
                    #     G = g
                    #     candidate = road_id
                    g_dict[road_id] = g
        # print(candidate)          
        g_dict_sorted = sort_dict_by_value(g_dict)
        top_g = list(g_dict_sorted.keys())[:3]
        
        return candidate, vertical_projection_lng, vertical_projection_lat, top_g