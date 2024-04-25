# import the folium, pandas libraries
import folium
import pandas as pd
import matplotlib.pyplot as plt

# initialize the map and store it in a m object
m = folium.Map(location = [40, -95],
			zoom_start = 4)

# show the map
m.save('my_map.html')
