import numpy as np
from numpy import exp
import pandas as pd
from math import radians, sin, cos, atan, atan2, sqrt, asin, degrees, pi, isnan
    
    
def degrees_to_radians(lat_1, lng_1, lat_2, lng_2):
    return map(radians, [lat_1, lng_1, lat_2, lng_2])

def haversine_distance(lat_1, lng_1, lat_2, lng_2): 
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1 
    
    temp = (sin(d_lat / 2) ** 2
          + cos(lat_1) 
          * cos(lat_2) 
          * sin(d_lng / 2) ** 2
          )
    return 6371.0 * (2 * atan2(sqrt(temp), sqrt(1 - temp))) * 1000

def euclidean_distance(lat_1, lng_1, lat_2, lng_2):
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1 
    
    return 6371.0 * sqrt(d_lat ** 2 + d_lng ** 2) * 1000
    

def azimuth(lat_1, lng_1, lat_2, lng_2):
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1 
    return atan2(d_lat, d_lng)

def point_to_line_distance(lat_1, lng_1, lat_2, lng_2, lat, lng):
    d_lat_1 = lat - lat_1
    d_lng_1 = lng - lng_1
    d_lat_2 = lat - lat_2
    d_lng_2 = lng - lng_2

    if (d_lat_1 * (lat_2 - lat_1) + d_lng_1 * (lng_2 - lng_1) < 0):
        return haversine_distance(lat, lng, lat_1, lng_1)

    if (d_lat_2 * (lat_1 - lat_2) + d_lng_2 * (lng_1 - lng_2) < 0):
        return haversine_distance(lat, lng, lat_2, lng_2)

    return abs(d_lat_1 * (lng_2 - lng_1) - d_lng_1 * (lat_2 - lat_1)) / sqrt((lng_2 - lng_1)**2 + (lat_2 - lat_1)**2) * 1000

def project_gps_point(x1, y1, x2, y2, x0, y0):
    slope = (y2 - y1) / (x2 - x1)
    y_intercept = y1 - slope * x1
    # d = abs(slope * x0 - y0 + y_intercept) / math.sqrt(slope**2 + 1)
    x_proj = (slope * (y0 - y_intercept) + x0) / (slope**2 + 1)
    y_proj = slope * x_proj + y_intercept
    return x_proj, y_proj

def on_line_check(lat_1, lng_1, lat_2, lng_2, lat, lng):
    seg_dist = haversine_distance(lat_1, lng_1, lat, lng) + haversine_distance(lat_2, lng_2, lat, lng) 
    return seg_dist - haversine_distance(lat_1, lng_1, lat_2, lng_2)

def sort_dict_by_value(dic):
    return dict(sorted(dic.items(), key=lambda item: item[1], reverse=False))

def list_traj(traj):
    df = traj.dropna()
    return list(df.trajID)

def intercept_slope(delta_distance, delta_time, v_i, v_j):
    ax = [[delta_time ** 2, (delta_time ** 2)/2], [(delta_time**2)/2, (delta_time**3)/6]]
    bx = [v_j - v_i, delta_distance - v_i * delta_time]
    intercept, slope = np.linalg.solve(ax, bx)
    return intercept, slope

def acceleration(intercept, slope, delta_time):
    return intercept + slope * delta_time

def acc_velocity(intercept, slope, delta_time, v_i):
    return v_i + intercept*delta_time + (slope/2)*(delta_time ** 2)

def dis_position(lat_1, lng_1, lat_2, lng_2, distance):
    distance = distance / 1000
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    
    theta = atan2(sin(lng_2 - lng_1) * cos(lat_2), cos(lat_1) * sin(lat_2) - sin(lat_1) * cos(lat_2) * cos(lng_2 - lng_1))

    
    lat = asin(sin(lat_1) * cos(distance / 6371.0) + 
                cos(lat_1) * sin(distance / 6371.0) * cos(theta))

    lng = lng_1 + atan2(sin(theta) * sin(distance / 6371.0) * cos(lat_1),
                        cos(distance / 6371.0) - sin(lat_1) * sin(lat))
    
    return degrees(lat), degrees(lng)
    
def segment_direction(lat_1, lng_1, lat_2, lng_2):
    if lat_2 > lat_1:
        return ((pi / 2) - atan((lng_2 - lng_1) / (lat_2 - lat_1))) * (180 / pi)
    elif lat_2 < lat_1:
        return ((3 * pi / 2) - atan((lng_2 - lng_1) / (lat_2 - lat_1))) * (180 / pi)
    else:
        return 0 if lat_2 == lat_1 else 180
        
def azimuth_point(lat, lng):
    north_lat = radians(90)
    north_lng = radians(0)
    lat = radians(lat)
    lng = radians(lng)
    
    d_lng = north_lng - lng
    y = sin(d_lng) * cos(north_lat)
    x = cos(lat) * sin(north_lat) - sin(lat) * cos(north_lat) * cos(d_lng)
    
    # azp = (degrees(atan2(y, x)) + 360) % 360 # Convert negative azimuth to positive value
    azp = (360 - degrees(atan2(y, x))) % 360 
    return azp
    
def azimuth_link(lat_1, lng_1, lat_2, lng_2):
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    
    d_lng = lng_2 - lng_1 
    y = sin(d_lng) * cos(lat_2)
    x = cos(lat_1) * sin(lat_2) - sin(lat_1) * cos(lat_2) * cos(d_lng)
    
    azl = (degrees(atan2(y, x)) + 360) % 360 # Convert negative azimuth to positive value
    return azl

def coor_position(lat_1, lng_1, lat_2, lng_2, distance, len_segment):
    distance = distance / (1000 * 6371.0)
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    alpha = distance / len_segment
    
    lat = alpha * (lat_2 - lat_1) + lat_1
    lng = alpha * (lng_2 - lng_1) + lng_1
    
    return degrees(lat), degrees(lng)
    