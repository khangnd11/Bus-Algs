from math import radians, sin, cos, atan2, sqrt

def degrees_to_radians(lat_1, lng_1, lat_2, lng_2):
    """
    Convert latitude and longitude from degrees to radians.

    Parameters:
    - lat_1, lng_1: Latitude and longitude of the first point
    - lat_2, lng_2: Latitude and longitude of the second point

    Returns:
    Tuple of radians for lat_1, lng_1, lat_2, lng_2
    """
    return map(radians, [lat_1, lng_1, lat_2, lng_2])

def haversine_distance(lat_1, lng_1, lat_2, lng_2): 
    """
    Calculate the Haversine distance between two points on the Earth's surface.

    Parameters:
    - lat_1, lng_1: Latitude and longitude of the first point
    - lat_2, lng_2: Latitude and longitude of the second point

    Returns:
    Haversine distance in meters between the two points.
    """
    # Convert latitude and longitude to radians
    lat_1, lng_1, lat_2, lng_2 = degrees_to_radians(lat_1, lng_1, lat_2, lng_2)
    
    # Calculate differences in latitude and longitude
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1 
    
    # Haversine formula
    temp = (sin(d_lat / 2) ** 2
          + cos(lat_1) 
          * cos(lat_2) 
          * sin(d_lng / 2) ** 2
          )
    
    # Calculate the distance using the Earth's radius
    return 6371.0 * (2 * atan2(sqrt(temp), sqrt(1 - temp))) * 1000
