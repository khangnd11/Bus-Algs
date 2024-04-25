import pandas as pd
import matplotlib.pyplot as plt
from utils import *

class Matching:
    def __init__(self, nodes, links, sigma=20, error_radius=100):
        self.num_link = len(links)
        self.nodes_dict = nodes.set_index('nodeID').T.to_dict('list')
        self.links_dict = links.set_index('linkID').T.to_dict('list')
        self.sigma = sigma
        self.error_radius = error_radius
    
    def spatial_probability(self, trajID, linkID):
        start_node_lat = self.nodes_dict[self.links_dict[linkID][0]][0]
        start_node_lng = self.nodes_dict[self.links_dict[linkID][0]][1]
        end_node_lat = self.nodes_dict[self.links_dict[linkID][1]][0]
        end_node_lng = self.nodes_dict[self.links_dict[linkID][1]][1]
        
        vertical_projection_lat, vertical_projection_lng = project_gps_point(start_node_lat,
                                                                             start_node_lng,
                                                                             end_node_lat,
                                                                             end_node_lng,
                                                                             trajID.latitude,
                                                                             trajID.longitude)
        # within error radius
        disp_3 = haversine_distance(trajID.latitude,trajID.longitude, vertical_projection_lat, vertical_projection_lng)
        # caculate distance
        disp_1 = haversine_distance(trajID.latitude,trajID.longitude, start_node_lat, start_node_lng)
        disp_2 = haversine_distance(trajID.latitude,trajID.longitude, end_node_lat, end_node_lng)
        
        H = min(disp_1, disp_2, disp_3)
        G_1 = 1 / (sqrt(2 * pi) * self.sigma) * exp(- (H ** 2) / (2 * (self.sigma ** 2)))
        
        return G_1
    
    def in_map_distance(self, trajID_1, trajID_2):
        # map_latitude map_longitude matched_link
        if trajID_1[2] == trajID_2[2]:
            return haversine_distance(trajID_1[0], trajID_1[1],
                                      trajID_2[0], trajID_2[1])
        else:
            s_node = self.links_dict[trajID_1[2]][1]
            e_node = self.links_dict[trajID_2[2]][0]
            lat = [trajID_1[0]] + [self.nodes_dict[node][0] for node in range(int(s_node), int(e_node))] + [trajID_2[0]]
            lng = [trajID_1[1]] + [self.nodes_dict[node][1] for node in range(int(s_node), int(e_node))] + [trajID_2[1]]
            
            dis = 0
            for inx in range(len(lat) - 1):
                dis += haversine_distance(lat[inx], lng[inx], lat[inx + 1], lng[inx + 1])
            
            return dis 
    
    def transmission_probability(self, pre, trajID, ver_lat, ver_lng, linkID):
        raw_dist = haversine_distance(pre[0], pre[1], trajID.latitude, trajID.longitude)
        map_dist = self.in_map_distance([pre[2], pre[3], pre[4]], [ver_lat, ver_lng, linkID])
        
        if raw_dist == 0 or map_dist == 0:
            G_2 = 0
        else:
            G_2 = raw_dist / map_dist
        
        return G_2
    
    def comprehensive_probability(self, pre, trajID, linkID, ver_lat, ver_lng):
        # return sqrt(self.spatial_probability(trajID, linkID) * self.directional_probability(trajID, linkID, nex_TrajID))
        return sqrt(self.spatial_probability(trajID, linkID) * self.transmission_probability(pre, trajID, ver_lat, ver_lng, linkID))
    
    def candidate_preparation(self, traj):
        candidate_sets = pd.DataFrame([], columns=['trajID', 'map_latitude', 'map_longitude', 'matched_link'])
        num_traj = len(traj)
        pre = []
        
        for inx in range(num_traj):
            candidate = None
            if isnan(traj.loc[inx, 'latitude']) or isnan(traj.loc[inx, 'longitude']):
                map_lat = None
                map_lng = None
            else:
                trajID = traj.loc[inx,]
                G = 0
                for linkID in range(self.num_link):
                    start_node_lat = self.nodes_dict[self.links_dict[linkID][0]][0]
                    start_node_lng = self.nodes_dict[self.links_dict[linkID][0]][1]
                    end_node_lat = self.nodes_dict[self.links_dict[linkID][1]][0]
                    end_node_lng = self.nodes_dict[self.links_dict[linkID][1]][1]
            
                    vertical_projection_lat, vertical_projection_lng = project_gps_point(start_node_lat,
                                                                                         start_node_lng,
                                                                                         end_node_lat,
                                                                                         end_node_lng,
                                                                                         trajID.latitude,
                                                                                         trajID.longitude)
                    # within error radius
                    dist = haversine_distance(trajID.latitude,trajID.longitude, vertical_projection_lat, vertical_projection_lng)
                    if dist <= self.error_radius:
                        s2e = self.links_dict[linkID][2]
                        s2v = haversine_distance(start_node_lat, start_node_lng, vertical_projection_lat, vertical_projection_lng)
                        v2e = haversine_distance(vertical_projection_lat, vertical_projection_lng, end_node_lat, end_node_lng)
                        if round(abs(s2e - s2v - v2e), 5) == 0.0:
                            # the firs GPS point is always correct and reliable
                            if inx == 0:
                                candidate = linkID
                                break
                            else:
                                g = self.comprehensive_probability(pre, trajID, linkID, vertical_projection_lat, vertical_projection_lng)
                                if g >= G:
                                    G = g
                                    candidate = linkID
                if candidate is None:
                    map_lat = None
                    map_lng = None
                else:
                    map_lat, map_lng = project_gps_point(self.nodes_dict[self.links_dict[candidate][0]][0],
                                                        self.nodes_dict[self.links_dict[candidate][0]][1],
                                                        self.nodes_dict[self.links_dict[candidate][1]][0],
                                                        self.nodes_dict[self.links_dict[candidate][1]][1],
                                                        trajID.latitude, 
                                                        trajID.longitude)
                    pre = [trajID.latitude, trajID.longitude, map_lat, map_lng, candidate]
            
            res = {'trajID': traj.loc[inx, 'trajID'], 'map_latitude': map_lat, 'map_longitude': map_lng, 'matched_link': candidate}
            res_df = pd.DataFrame(res, index=[0]) 
            candidate_sets = pd.concat([candidate_sets, res_df], ignore_index=True)
             
        return pd.merge(traj, candidate_sets, on='trajID', how='inner')
        
    def direction_analysis(self, traj):
        direction_sets = traj
        num_traj = len(traj)
        pre = [0] 
        for inx in range(1, num_traj):
            if not isnan(direction_sets.loc[inx, 'map_latitude']):
                if direction_sets.loc[inx, 'matched_link'] < direction_sets.loc[pre[-1], 'matched_link']:
                    direction_sets.loc[inx, 'map_latitude'] = direction_sets.loc[pre[-1], 'map_latitude']
                    direction_sets.loc[inx, 'map_longitude'] = direction_sets.loc[pre[-1], 'map_longitude']
                    direction_sets.loc[inx, 'matched_link'] = direction_sets.loc[pre[-1], 'matched_link']
                    
                elif direction_sets.loc[inx, 'matched_link'] == direction_sets.loc[pre[-1], 'matched_link']:
                    if pre[-1] == 0:
                        dist1 = haversine_distance(self.nodes_dict[direction_sets.loc[0, 'matched_link']][0],
                                                self.nodes_dict[direction_sets.loc[0, 'matched_link']][1],
                                                direction_sets.loc[inx, 'map_latitude'],
                                                direction_sets.loc[inx, 'map_longitude'])
                        
                        dist2 = haversine_distance(self.nodes_dict[direction_sets.loc[0, 'matched_link']][0],
                                                self.nodes_dict[direction_sets.loc[0, 'matched_link']][1],
                                                direction_sets.loc[pre[-1], 'map_latitude'],
                                                direction_sets.loc[pre[-1], 'map_longitude'])
                    else:
                        dist1 = haversine_distance(direction_sets.loc[pre[-2], 'map_latitude'],
                                                direction_sets.loc[pre[-2], 'map_longitude'],
                                                direction_sets.loc[inx, 'map_latitude'],
                                                direction_sets.loc[inx, 'map_longitude'])
                        
                        dist2 = haversine_distance(direction_sets.loc[pre[-1], 'map_latitude'],
                                                direction_sets.loc[pre[-1], 'map_longitude'],
                                                direction_sets.loc[inx, 'map_latitude'],
                                                direction_sets.loc[inx, 'map_longitude'])
                        
                    if dist1 < dist2:
                        print(f"Direction Error: {inx} -- {dist1} -- {dist2}")
                        direction_sets.loc[inx, 'map_latitude'] = direction_sets.loc[pre[-1], 'map_latitude']
                        direction_sets.loc[inx, 'map_longitude'] = direction_sets.loc[pre[-1], 'map_longitude']
                pre.append(inx)
        
        return direction_sets
    
    def map_matching(self, traj):
        matching = self.candidate_preparation(traj)
        matching = self.direction_analysis(matching)
        
        return matching
                
    def viz(self, traj):
        len_traj = len(traj)
        for inx in range(0, len_traj, 10):
            df = traj.loc[inx:inx+10]
            
            traj_lat = list(df.latitude)
            traj_lng = list(df.longitude)
            map_lat = list(df.map_latitude)
            map_lng = list(df.map_longitude)
            
            trajIDs = list(df.trajID)
            links = list(set(list(df.matched_link))) 
            s_node = self.links_dict[min(links)][0]
            e_node = self.links_dict[max(links)][1] 
            
            node_lat = [self.nodes_dict[node][0] for node in range (s_node, e_node)]
            node_lng = [self.nodes_dict[node][1] for node in range (s_node, e_node)]
            
            plt.figure(figsize=(19,6), facecolor='white')
            plt.plot(node_lng, node_lat, '*', markersize=8, color='blue')
            plt.plot(node_lng, node_lat, markersize=5, color='blue')
            plt.scatter(traj_lng, traj_lat, color='red')
            plt.plot(traj_lng, traj_lat, markersize=5, color='orange')
            for i, label in enumerate(trajIDs):
                plt.annotate(label, (traj_lng[i], traj_lat[i]))
                plt.annotate(label, (map_lng[i], map_lat[i]))
           
            plt.plot(map_lng, map_lat, '*', markersize=8, color='green')
            plt.plot(map_lng, map_lat, markersize=5, color='green')
            plt.title(f"{inx} - {inx+10}")
            plt.show()