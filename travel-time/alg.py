import pandas as pd
import numpy as np

from V_clustering import V_clustering

# from multiprocessing import Process
# from sklearn.cluster import DBSCAN
 
class Bus_TravelTime():
    def __init__(self, MNT, MNC, Vthresh_temp, Vthresh_pass, historical_trajectory):
        self.MNT = MNT # Minimum Number of Trajectories
        self.MNC = MNC # Maximum Number of  Clustering
        self.Vthresh_temp = Vthresh_temp # Tunable Threshold for temporal similarities
        self.Vthresh_pass = Vthresh_pass # Tunable Threshold for pass segmentation
        self.all_historical_trajectory = historical_trajectory # Historical Bus Trajectories
        
        self.historical_trajectory = None
    
    def get_historical_trajectory(self):
        self.historical_trajectory = self.all_historical_trajectory
        # print("--> Historical Trajectories: Got")
    
    def update_historical_trajectory(self, TripId_list):
        self.historical_trajectory = self.all_historical_trajectory[self.all_historical_trajectory.TripId.isin(TripId_list)]
    
    # return list segment Id of this route
    def get_list_segmentId(self):
        id = self.historical_trajectory.iloc[0]['TripId']
        temp = self.historical_trajectory[self.historical_trajectory.TripId == id]
        list_segmentId = list(temp.SegmentId)
        
        return list_segmentId
    
    # get segments by seg_start_timme (time in day) 
    def segs_temp(self, SegmentId, temp):
        segs = self.historical_trajectory[self.historical_trajectory.SegmentId == SegmentId] 
        # in_range = segs.StartSeg.std()
        # in_range = segs.StartSeg.mean()
        in_range = 900
        segs = segs[(segs.StartSeg >= (temp - in_range)) &
                    (segs.StartSeg <= (temp + in_range))]
        
        trips = list(segs.TripId)
        return trips
    
    # temporal clustering
    def temporal_similar_cluster(self, TripId_list, SegmentId, predicted_trip):
        trips = self.historical_trajectory[(self.historical_trajectory.TripId.isin(TripId_list)) &
                                           (self.historical_trajectory.SegmentId == SegmentId)]
        
        trips.loc[len(trips)] = predicted_trip
        trips = trips.sort_values(by=['StartSeg'])
        
        trips['label'] = V_clustering(L=trips['StartSeg'], Vthresh=self.Vthresh_temp)
        label = trips[trips.TripId==0].iloc[0]['label']
        similar_trips = list (trips[trips.label == label].TripId)
        similar_trips.remove(0)
        
        return similar_trips
    
    # get segments by duration
    def segs_pass(self, SegmentId, dura):
        segs = self.historical_trajectory[self.historical_trajectory.SegmentId == SegmentId] 
        # in_range = segs.Duration.std()
        in_range = 900
        segs = segs[(segs.Duration >= (dura - in_range)) &
                    (segs.Duration <= (dura + in_range))]
        
        trips = list(segs.TripId)
        return trips
    
    def pass_segment_cluster(self, TripId_list, SegmentId, predicted_trip):
        trips = self.historical_trajectory[(self.historical_trajectory.TripId.isin(TripId_list)) &
                                           (self.historical_trajectory.SegmentId == SegmentId)]
        trips.loc[len(trips)] = predicted_trip
        trips = trips.sort_values(by=['Duration'])
        
        trips['label'] = V_clustering(L=trips['Duration'], Vthresh=self.Vthresh_pass)
        label = trips[trips.TripId==0].iloc[0]['label']
        similar_trips = list(trips[trips.label == label].TripId)
        similar_trips.remove(0)
        
        return similar_trips
    
    def duration_prediction(self, SegmentId):
        segs = self.historical_trajectory[self.historical_trajectory.SegmentId == SegmentId]
        dura = segs['Duration'].mean()
        
        return int(round(dura))
        
    def future_prediction(self, departure_time, seg_start, seg_end):
        self.get_historical_trajectory()
        all_segmentId = self.get_list_segmentId()
        ori_start = start = all_segmentId.index(seg_start)
        end = all_segmentId.index(seg_end)
        
        
        res = list()
        all_segment_durations = [0] * ori_start
        all_segment_starttime = [0] * ori_start
        total_durations = 0
        # [0, 'SegmentId', 'StartSeg', 'Duration']
        # predicted_trip = list()
        seg_start_time = departure_time
        
        # first segment, get trips with similar departture time
        # return list of tripId with similar departure time in seg_start
        trips = self.segs_temp(SegmentId=seg_start, temp=seg_start_time) #return list of tripId with similar departure time
        ini_similar_trips = self.temporal_similar_cluster(TripId_list=trips, SegmentId=seg_start, predicted_trip=[0, seg_start, departure_time, None])
        self.update_historical_trajectory(TripId_list=ini_similar_trips)
        
        dura = self.duration_prediction(SegmentId=seg_start)
        total_durations += dura
        res.append([0, seg_start, departure_time, dura])
        all_segment_durations.append(dura)
        all_segment_starttime.append(seg_start_time)
        
        # update next segment start time
        seg_start_time += dura
        all_segment_starttime.append(seg_start_time)
        
        start += 1
        while start <= end:
            self.update_historical_trajectory(TripId_list=ini_similar_trips)
            
            cur_seg = start
            cur_segmentId = all_segmentId[cur_seg]
            
            trips = self.segs_temp(SegmentId=cur_segmentId, temp=seg_start_time)
            similar_trips = self.temporal_similar_cluster(TripId_list=trips, SegmentId=cur_segmentId, predicted_trip=[0, cur_segmentId, seg_start_time, None])
            self.update_historical_trajectory(TripId_list=similar_trips)
            
            clustering_count = 1
            pass_seg = cur_seg - 1
            similar_pass_trips = similar_trips
            
            while (clustering_count <= self.MNC) and (len(similar_pass_trips) >= self.MNT) and (pass_seg > ori_start):
                pass_segmentId = all_segmentId[pass_seg]
                pass_trips = self.segs_pass(SegmentId=pass_segmentId, dura=all_segment_durations[pass_seg])
                similar_pass_trips = self.pass_segment_cluster(TripId_list=pass_trips, SegmentId=pass_segmentId, predicted_trip=[0, pass_segmentId, all_segment_starttime[pass_seg] , all_segment_durations[pass_seg]])
                clustering_count += 1
                pass_seg -= 1
            
            self.update_historical_trajectory(TripId_list=similar_pass_trips)
            dura = self.duration_prediction(SegmentId=cur_segmentId)
            total_durations += dura
            res.append([0, cur_segmentId, seg_start_time, dura])
            all_segment_durations.append(dura)
            start += 1
            seg_start_time += dura
            all_segment_starttime.append(seg_start_time)
        
        # [0, 'SegmentId', 'StartSeg', 'Duration']
        res_df = pd.DataFrame(res, columns=['TripId', 'SegmentId', 'StartSeg', 'Duration'])
        print(res_df)
        return total_durations
                
        
        # # update for next iteration
        # cur_seg += 1
        # pre_seg_start += duration
        # predict_traj = [trajID, cur_seg, start_time, duration, day_of_week, pre_seg_start]
        
        # while cur_seg <= seg_end:
        #     # self.get_his_trajs(day=day_of_week)
        #     self.get_his_trajs(day=day_of_week, tripID=tripID)
        #     similar_trajs = self.temporal_similar(segID=cur_seg, traj=predict_traj)
        #     self.update_his_trajs(similar_trips_id=similar_trajs)
            
        #     backup_trajs = similar_trajs
        #     clustering_count = 1
        #     while (clustering_count <= self.MNC) and (len(similar_trajs) >= self.MNT) and (pas_seg > 0):
        #         backup_trajs = similar_trajs
        #         self.update_his_trajs(similar_trips_id=similar_trajs)
        #         similar_trajs = self.pass_segment(segID=pas_seg, traj=predict_traj)
        #         # if len(similar_trajs) != 0:
        #         #     similar_trajs = self.segment_duration_similar(segID=pas_seg, similar_trajs=similar_trajs)
        #         # update for nexr cluster
        #         clustering_count += 1
        #         pas_seg -= 1
                
        #     if len(similar_trajs) < self.MNT:
        #             similar_trajs = backup_trajs 
        #             self.update_his_trajs(similar_trips_id=similar_trajs)
                
        #     duration = self.predict_duration(segID=cur_seg, similar_trajs=similar_trajs)
        #     predict_traj = [trajID, cur_seg, start_time, duration, day_of_week, pre_seg_start]
        #     res_df.loc[len(res_df)] = predict_traj
        #     # update for next iteration
        #     pas_seg = cur_seg
        #     cur_seg +=1
        #     pre_seg_start += duration
        #     predict_traj = [trajID, cur_seg, start_time,  duration, day_of_week, pre_seg_start]
            
        # res_df = pd.DataFrame(res, columns=['TripId', 'Date', 'SegmentId', 'StartSeg', 'Duration'])
        # return res_df
    
    
    