import folium
import pandas as pd 
from tqdm import tqdm 
import requests
import json
import Location

def get_marker_color(value):
    if value < 1000:
        return 'green'
    elif value < 2000:
        return 'orange'
    else:
        return 'red'
    

data2 = pd.read_csv("../clean data/hotel_clean.csv")
data = data2.sample(n=500, random_state=1)
lats = []
longs = []
for i in tqdm(range(len(data))):
    lat = Location(data.iloc[i]["Address"].split(",")[0] + " Đà Nẵng Việt Nam").get_lat()
    long = Location(data.iloc[i]["Address"].split("," )[0] + " Đà Nẵng Việt Nam").get_long()
    lats.append(lat)
    longs.append(long)
data["lat"] = lats
data["lon"] = longs
marker_group = folium.FeatureGroup(name='Markers')


for i in range(0,len(data)):
    latitude = data.iloc[i]['lat']
    longitude = data.iloc[i]['lon']
    value = float(data.iloc[i]['Price'])
    marker_color = get_marker_color(value)
    map = folium.Map(location=[latitude, longitude], zoom_start=13)
    # Thêm đánh dấu tại tọa độ cụ thể
    popup_text = f"Location: <br>Latitude: {latitude}<br>Longitude: {longitude}"
    marker_icon = folium.Icon(color=marker_color)
    folium.Marker([latitude, longitude], popup=popup_text, icon=marker_icon).add_to(marker_group)
# Hiển thị bản đồ
marker_group.add_to(map)
map.save('map.html')