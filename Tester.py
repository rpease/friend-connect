from FakeDatabaseAPI import *
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import branca
import numpy as np
import json

def get_folium_radius(min,max,value):
    max_radius = 50.0
    min_radius = 0.0
    slope = max_radius-min_radius

    return (value-min)/(max-min)*slope + min_radius

def plot_cities(data, map):
    x_data = []
    y_data = []
    f_data = []
    xyf_data = []    

    # Add Cities to Map
    for city in self._cities:
        x_data.append(city.Get_Longitude())
        y_data.append(city.Get_Latitude())
        f_data.append(city.Get_Score())
        po

        xyf_data.append([city.Get_Latitude(),city.Get_Longitude(),city.Get_Score()])

    color_map = branca.colormap.linear.YlOrRd_09.scale(np.average(f_data),max(f_data))  

    for i in range(len(x_data)):
        color_code = color_map(f_data[i])
        folium.CircleMarker(location=[y_data[i],x_data[i]],
            fill=True,
            color=color_code,
            fill_color=color_code,
            radius=get_folium_radius(["metadata"]["min_score"],["metadata"]["max_score"],f_data[i]),
            popup=self._cities[i].Get_Description()).add_to(map)

def plot_users(data, map):
    # Add users to map
    for user in self._users:
        coord = user.Get_Location()
        x_data_user.append(coord.Get_Longitude())
        y_data_user.append(coord.Get_Latitude())

    for i in range(len(y_data_user)):
        folium.Marker(location=[y_data_user[i],x_data_user[i]],
            popup=self._users[i]._name).add_to(folium_map)

    # Add Geographical Center of Users        
    folium.Marker(location=[lat,lon],
        popup="Geographical Center of Users",
        icon=folium.Icon(color='green')).add_to(folium_map)

def plot_results(score_json: str):
        
        x_data_user = []
        y_data_user = []

        data = json.loads(score_json)

        folium_map = folium.Map(location=[data["metadata"]["center"]["latitude"],data["metadata"]["center"]["longitude"]],zoom_start=7,tiles="CartoDB dark_matter")

        plot_cities(data,folium_map)     
        plot_users(data,folium_map)        

        folium_map.save("Map.html")
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("Map.html",new=1)
        os.remove("Map.html")

fakeAPI = FakeDatabaseAPI(r"test_data\city15000.csv","")
fakeAPI.load_users_table(r"test_data\users.csv")
fakeAPI.load_weight_table(r"test_data\weights.txt")

data = fakeAPI.get_user_destination_distance_matrix(True)
data = fakeAPI.get_scores(0)

plot_results(data)

print("done")