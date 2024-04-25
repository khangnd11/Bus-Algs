import numpy as np
from datetime import datetime
from utils import *

class Kinematic():
    def __init__(self, nodes, links):
        self.num_link = len(links)
        self.nodes_dict = nodes.set_index('nodeID').T.to_dict('list')
        self.links_dict = links.set_index('linkID').T.to_dict('list')
        
    def intercept_slope(self, delta_distance, delta_time, v_i, v_j):
        ax = [[delta_time ** 2, (delta_time ** 2)/2], [(delta_time ** 2)/2, (delta_time ** 3)/6]]
        bx = [v_j - v_i, delta_distance - v_i * delta_time]
        intercept, slope = np.linalg.solve(ax, bx)
        return intercept, slope # b, m
    
    def in_map_distance(self, trajID_1, trajID_2):
        if trajID_1.matched_link == trajID_2.matched_link:
            return haversine_distance(trajID_1.map_latitude, trajID_1.map_longitude,
                                      trajID_2.map_latitude, trajID_2.map_longitude)
        else:
            s_node = self.links_dict[trajID_1.matched_link][1]
            e_node = self.links_dict[trajID_2.matched_link][0]
            lat = [trajID_1.map_latitude] + [self.nodes_dict[node][0] for node in range(int(s_node), int(e_node))] + [trajID_2.map_latitude]
            lng = [trajID_1.map_longitude] + [self.nodes_dict[node][1] for node in range(int(s_node), int(e_node))] + [trajID_2.map_longitude]
            dis = 0
            for inx in range(0, len(lat) - 1):
                dis += haversine_distance(lat[inx], lng[inx], lat[inx + 1], lng[inx + 1])
            return dis 
        
    def average_speed(self, trajID_1, trajID_2):
        delta_dis = self.in_map_distance(trajID_1, trajID_2)
        t_1 = trajID_1.time
        t_2 = trajID_2.time
        t_1 = datetime.strptime(t_1, "%H:%M:%S")
        t_2 = datetime.strptime(t_2, "%H:%M:%S")
        delta_time = (t_2 - t_1).total_seconds()
        return delta_dis / delta_time
    
    def next_trajID(self, pos, traj):
        num_traj = len(traj)
        for inx in range(pos + 1, num_traj):
            if not isnan(traj.loc[inx, 'map_latitude']):
                return inx
        
    def kinematic(self, traj):
        num_traj = len(traj)
        imputed_sets = pd.DataFrame([], columns=['trajID', 'imp_latitude', 'imp_longitude', 'imp_link'])
        res = {'trajID': traj.loc[0, 'trajID'],
               'imp_latitude': traj.loc[0, 'map_latitude'],
               'imp_longitude': traj.loc[0, 'map_longitude'],
               'imp_link': traj.loc[0, 'matched_link']}
        res_df = pd.DataFrame(res, index=[0]) 
        imputed_sets = pd.concat([imputed_sets, res_df], ignore_index=True)
        pre = 0
        for inx in range(1, num_traj):
            if not isnan(traj.loc[inx, 'map_latitude']):
                pre = inx
                res = {'trajID': inx,
                        'imp_latitude': traj.loc[inx, 'map_latitude'],
                        'imp_longitude': traj.loc[inx, 'map_longitude'],
                        'imp_link': traj.loc[inx, 'matched_link']}
                res_df = pd.DataFrame(res, index=[0]) 
                imputed_sets = pd.concat([imputed_sets, res_df], ignore_index=True)
            else:
                i = pre
                j = self.next_trajID(pre, traj)
                avg_speed = self.average_speed(traj.loc[i, ], traj.loc[j, ])
                t_i = traj.loc[i, 'time']
                t_i = datetime.strptime(t_i, "%H:%M:%S")
                t_u = traj.loc[inx, 'time']
                t_u = datetime.strptime(t_u, "%H:%M:%S")
                travel_time = (t_u - t_i).total_seconds()
                travel_distance = travel_time * avg_speed
                
                imp_link = traj.loc[i, 'matched_link']
                s_node = self.links_dict[imp_link][0]
                e_node = self.links_dict[imp_link][1] 
                if traj.loc[i, 'matched_link'] == traj.loc[j, 'matched_link']:
                    to_node_distance = haversine_distance(self.nodes_dict[s_node][0],
                                                        self.nodes_dict[s_node][1],
                                                        traj.loc[i, 'map_latitude'],
                                                        traj.loc[i, 'map_longitude'])
                    L = to_node_distance + travel_distance
                    imp_lat, imp_lng = dis_position(self.nodes_dict[s_node][0],
                                                 self.nodes_dict[s_node][1],
                                                 self.nodes_dict[e_node][0],
                                                 self.nodes_dict[e_node][1],
                                                 L)
                else:
                    to_node_distance = haversine_distance(traj.loc[i, 'map_latitude'],
                                                          traj.loc[i, 'map_longitude'],
                                                          self.nodes_dict[e_node][0],
                                                          self.nodes_dict[e_node][1])
                    travel_distance = travel_distance - to_node_distance
                    imp_link += 1
                    while travel_distance > self.links_dict[imp_link][2]:
                        travel_distance = travel_distance - self.links_dict[imp_link][2]
                        imp_link += 1
                    s_node = self.links_dict[imp_link][0]
                    e_node = self.links_dict[imp_link][1] 
                    imp_lat, imp_lng = dis_position(self.nodes_dict[s_node][0],
                                                 self.nodes_dict[s_node][1],
                                                 self.nodes_dict[e_node][0],
                                                 self.nodes_dict[e_node][1],
                                                 travel_distance)
                res = {'trajID': inx,
                        'imp_latitude': imp_lat,
                        'imp_longitude': imp_lng,
                        'imp_link': imp_link}
                res_df = pd.DataFrame(res, index=[0]) 
                imputed_sets = pd.concat([imputed_sets, res_df], ignore_index=True)
        return pd.merge(traj, imputed_sets, on='trajID', how='inner')
    
    # def kinematic_inter_slope(self, traj):
    #     num_traj = len(traj)
    #     imputed_sets = pd.DataFrame([], columns=['trajID', 'imp_latitude', 'imp_longitude', 'imp_link'])
    #     res = {'trajID': traj.loc[0, 'trajID'],
    #            'imp_latitude': traj.loc[0, 'map_latitude'],
    #            'imp_longitude': traj.loc[0, 'map_longitude'],
    #            'imp_link': traj.loc[0, 'matched_link']}
    #     res_df = pd.DataFrame(res, index=[0]) 
    #     imputed_sets = pd.concat([imputed_sets, res_df], ignore_index=True)
    #     pre = [0]
        
    #     for inx in range(1, num_traj):
    #         if not isnan(traj.loc[inx, 'map_latitude']):
    #             pre.append(inx)
    #             res = {'trajID': inx,
    #                     'imp_latitude': traj.loc[inx, 'map_latitude'],
    #                     'imp_longitude': traj.loc[inx, 'map_longitude'],
    #                     'imp_link': traj.loc[inx, 'matched_link']}
    #             res_df = pd.DataFrame(res, index=[0]) 
    #             imputed_sets = pd.concat([imputed_sets, res_df], ignore_index=True)
    #         else:
    #             # pre --> i --> u --> j
    #             i = pre[-1]
    #             if pre[-1] == 0:
    #                 v_i = 0
    #             else:
    #                 v_i = self.average_speed(traj.loc[pre[-2], ], traj.loc[pre[-1], ])
    #             j = self.next_trajID(inx, traj)
    #             if j == (num_traj - 1):
    #                 v_j = 0
    #             else:
    #                 v_j = self.average_speed(traj.loc[pre[-1], ], traj.loc[j, ])
                    
    #             delta_distance = self.in_map_distance(traj.loc[i, ], traj.loc[j, ])
                
    #             t_i = traj.loc[i, 'time']
    #             t_i = datetime.strptime(t_i, "%H:%M:%S")
    #             t_j = traj.loc[j, 'time']
    #             t_j = datetime.strptime(t_j, "%H:%M:%S")
    #             delta_time = (t_j - t_i).total_seconds()
                
    #             intercept, slope = self.intercept_slope(delta_distance,
    #                                                     delta_time,
    #                                                     v_i,
    #                                                     v_j)
                
    #             t_u = traj.loc[inx, 'time']
    #             t_u = datetime.strptime(t_u, "%H:%M:%S")
    #             imp_delta_time = (t_u - t_i).total_seconds()
                
    #             v_u = v_i + intercept * imp_delta_time + (slope / 2) * (imp_delta_time ** 2)
                
                
    #             L = v_i * imp_delta_time + \
    #                 (intercept / 2) * (imp_delta_time ** 2) + \
    #                 (slope / 6) * (imp_delta_time ** 3)
                
                    
    #             imp_link = traj.loc[i, 'matched_link']
    #             s_node = self.links_dict[imp_link][0]
    #             e_node = self.links_dict[imp_link][1]
                
    #             if L < self.links_dict[imp_link][2]:
    #                 imp_lat, imp_lng = coor_position(self.nodes_dict[s_node][0],
    #                                              self.nodes_dict[s_node][1],
    #                                              self.nodes_dict[e_node][0],
    #                                              self.nodes_dict[e_node][1],
    #                                              L,
    #                                              self.links_dict[imp_link][2])
    #                 # imp_lat, imp_lng = dis_position(self.nodes_dict[s_node][0],
    #                 #                              self.nodes_dict[s_node][1],
    #                 #                              self.nodes_dict[e_node][0],
    #                 #                              self.nodes_dict[e_node][1],
    #                 #                              L)
    #             else:
    #                 L = L - haversine_distance(traj.loc[i, 'map_latitude'],
    #                                            traj.loc[i, 'map_longitude'],
    #                                            self.nodes_dict[e_node][0],
    #                                            self.nodes_dict[e_node][1])
    #                 imp_link += 1
    #                 while L > self.links_dict[imp_link][2]:
    #                     L = L - self.links_dict[imp_link][2]
    #                     imp_link += 1
                       
    #                 s_node = self.links_dict[imp_link][0]
    #                 e_node = self.links_dict[imp_link][1] 
                    
    #                 imp_lat, imp_lng = coor_position(self.nodes_dict[s_node][0],
    #                                              self.nodes_dict[s_node][1],
    #                                              self.nodes_dict[e_node][0],
    #                                              self.nodes_dict[e_node][1],
    #                                              L,
    #                                              self.links_dict[imp_link][2])
    #                 # imp_lat, imp_lng = dis_position(self.nodes_dict[s_node][0],
    #                 #                              self.nodes_dict[s_node][1],
    #                 #                              self.nodes_dict[e_node][0],
    #                 #                              self.nodes_dict[e_node][1],
    #                 #                              L)
                
    #             res = {'trajID': inx,
    #                     'imp_latitude': imp_lat,
    #                     'imp_longitude': imp_lng,
    #                     'imp_link': imp_link}
    #             res_df = pd.DataFrame(res, index=[0]) 
    #             imputed_sets = pd.concat([imputed_sets, res_df], ignore_index=True)
        
    #     return pd.merge(traj, imputed_sets, on='trajID', how='inner')