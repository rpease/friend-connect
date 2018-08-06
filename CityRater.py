from multipledispatch import dispatch
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import branca
import numpy as np
import os
import json
import urllib
import webbrowser
import math

class CityRater:

    driving_speed_kph = 112.65
	
    _cities: list
    users: list
    _weights: dict
    _valid_calculation = bool   


    def _google_estimate_API(self,city,user) :
        start = city.get_google_API_string()
        finish = user.get_coordinate().get_google_API_string()

        url = 'https://maps.googleapis.com/maps/api/distancematrix/json?%s' % urllib.parse.urlencode((
                    ('origins', start),
                    ('destinations', finish)
        ))

        tries = 50
        got_json = False
        try_attempt = 0
        while try_attempt < tries:            
            try:
                ur = urllib.request.urlopen(url)
                result = json.load(ur)
        
                driving_distance_meters = result["rows"][0]["elements"][0]["distance"]["value"]
                travel_time_minutes = result["rows"][0]["elements"][0]["duration"]["value"] / 60.0
                return (driving_distance_meters,travel_time_minutes)
            except:
                try_attempt += 1

        raise Exception("Couldn't complete Google API Request.")

    

    def plot_results(self):
        x_data = []
        y_data = []
        f_data = []
        xyf_data = []

        x_data_user = []
        y_data_user = []

        for city in self._cities:
            x_data.append(city.Get_Longitude())
            y_data.append(city.Get_Latitude())
            f_data.append(city.Get_Score())

            xyf_data.append([city.Get_Latitude(),city.Get_Longitude(),city.Get_Score()])

        for user in self._users:
            coord = user.Get_Location()
            x_data_user.append(coord.Get_Longitude())
            y_data_user.append(coord.Get_Latitude())

        lat,lon = self.Get_Geographical_Center()

        folium_map = folium.Map(location=[lat,lon],zoom_start=7,tiles="CartoDB dark_matter")

        color_map = branca.colormap.linear.YlOrRd_09.scale(np.average(f_data),max(f_data))

        # Add Cities to Map
        for i in range(len(x_data)):
            color_code = color_map(f_data[i])
            folium.CircleMarker(location=[y_data[i],x_data[i]],
                fill=True,
                color=color_code,
                fill_color=color_code,
                radius=f_data[i]*50.0,
                popup=self._cities[i].Get_Description()).add_to(folium_map)

        # Add users to map
        for i in range(len(y_data_user)):
            folium.Marker(location=[y_data_user[i],x_data_user[i]],
                popup=self._users[i]._name).add_to(folium_map)

        # Add Geographical Center of Users        
        folium.Marker(location=[lat,lon],
            popup="Geographical Center of Users",
            icon=folium.Icon(color='green')).add_to(folium_map)

        # Heat Map
        #HeatMap(xyf_data).add_to(folium_map)

        folium_map.save("Map.html")
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("Map.html",new=1)
        os.remove("Map.html")