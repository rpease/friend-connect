from FakeDatabaseAPI import *
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import branca
import numpy as np
import json
import os
import webbrowser
import time

def get_folium_radius(min,max,value):
    max_radius = 30.0
    min_radius = 1.0
    slope = max_radius-min_radius

    return (value-min)/(max-min)*slope + min_radius

def plot_cities(data, map):
    x_data = []
    y_data = []
    f_data = []
    name_data = []    

    # Add Cities to Map
    for name,info in data["city_scores"].items():
        x_data.append(info["longitude"])
        y_data.append(info["latitude"])
        f_data.append(info["score"])
        name_data.append(name)    

    color_map = branca.colormap.linear.YlOrRd_09.scale(np.average(f_data),max(f_data))  

    for i in range(len(x_data)):
        color_code = color_map(f_data[i])
        folium.CircleMarker(location=[y_data[i],x_data[i]],
            fill=True,
            color=color_code,
            fill_color=color_code,
            radius=get_folium_radius(data["metadata"]["min_score"],data["metadata"]["max_score"],f_data[i]),
            popup=name_data[i]).add_to(map)

    center_lat = data["metadata"]["center"]["latitude"]
    center_lon = data["metadata"]["center"]["longitude"]
    # Add Geographical Center of Users        
    folium.Marker(location=[center_lat,center_lon],
        popup="Geographical Center of Users",
        icon=folium.Icon(color='green')).add_to(map)

def plot_users(data, map):
    x_data = []
    y_data = []
    name_data = []  

    # Add users to map
    for name,info in data.items():
        
        x_data.append(info["longitude"])
        y_data.append(info["latitude"])
        name_data.append(name)

    for i in range(len(y_data)):
        folium.Marker(location=[y_data[i],x_data[i]],
            popup=name_data[i]).add_to(map)


def plot_results(score_json: str, user_json: str):
        
        x_data_user = []
        y_data_user = []

        data = json.loads(score_json)
        user_data = json.loads(user_json)

        folium_map = folium.Map(location=[data["metadata"]["center"]["latitude"],data["metadata"]["center"]["longitude"]],zoom_start=7,tiles="CartoDB dark_matter")

        plot_cities(data,folium_map)     
        plot_users(user_data,folium_map)        

        folium_map.save("Map.html")
        #webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("Map.html",new=1)
        webbrowser.open("Map.html")
        time.sleep(1.0)
        os.remove("Map.html")

session_id = 0

fakeAPI = FakeDatabaseAPI(r"test_data\city15000.csv","")
fakeAPI.load_users_table(r"test_data\users.csv")
fakeAPI.load_weight_table(r"test_data\weights.txt")

data = fakeAPI.get_user_destination_distance_matrix(True)
data = fakeAPI.get_scores(session_id)

user_data = fakeAPI.get_user_data_json(session_id);

plot_results(data,user_data)

print("done")