from multipledispatch import dispatch
from Friend import *
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import branca
import numpy as np
import os
import json
import urllib

class CityRater:
    
    def __init__(self,cities,users = []):
        self._cities = cities
        self.Set_Users(users)
        self._Initialize_Weights()
        self._valid_calculation = False

    def _Initialize_Weights(self):
        self._weights = {}
        self.Set_Haversine_Weight(1.0)
        self.Set_Population_Weight(1.0)
        self.Set_Travel_Time_Weight(1.0)
        self.Set_Drive_Distance_Weight(1.0)

    @dispatch(Friend)
    def Add_User(self,user):
        self._valid_calculation = False
        self._users.append(user)

    @dispatch(list)
    def Add_Users(self,users):
        for user in users:
            self.Add_User(user)

    def Set_Users(self,users):
        self._valid_calculation = False
        self._users = users

    def Get_Top_Cities(self,num = 10):
        if not self._valid_calculation:
            self._Calculate_Scores()
        self._cities.sort(reverse=True)
        return self._cities[:num]

    def Set_Haversine_Weight(self,weight):
        self._valid_calculation = False
        self._weights["hav"] = weight

    def Set_Population_Weight(self,weight):
        self._valid_calculation = False
        self._weights["pop"] = weight

    def Set_Travel_Time_Weight(self,weight):
        self._valid_calculation = False
        self._weights["time"] = weight

    def Set_Drive_Distance_Weight(self,weight):
        self._valid_calculation = False
        self._weights["drive"] = weight

    def _Score_Function(self,city):
        score = self._weights["pop"]*city.Get_NormScore("pop") - self._weights["hav"]*city.Get_NormScore("hav") - self._weights["time"]*city.Get_NormScore("time") - self._weights["drive"]*city.Get_NormScore("drive")
        if score < 0:
            score = 0.0
        return score

    def _Calculate_Scores(self):

        max_dict = {}
        max_dict["pop"] = 0.0
        max_dict["hav"] = 0.0
        max_dict["time"] = 0.0
        max_dict["drive"] = 0.0

        distance_matrix,time_matrix = self._Google_Estimate_API_Matrix()

        # Get Pre-Normalized Values
        for c in range(len(self._cities)):
            city = self._cities[c]
            city_name = city._name  
            print(city_name)
            population = math.log10(city.Get_Population())
            average_distance = 0.0
            average_driving_time_min = 0.0
            average_driving_distance_m = 0.0

            for u in range(len(self._users)):
                user = self._users[u]
                average_distance += city.Get_Distance_Km(user)

                #driving_distance_m,travel_time_min = self.Get_Driving_Directions(city.Get_Coordinate(),user.Get_Location())
                #average_driving_time_min += travel_time_min
                #average_driving_distance_m += driving_distance_m
                                 
                average_driving_time_min += time_matrix[c][u]
                average_driving_distance_m += distance_matrix[c][u]

            average_distance /= len(self._users)
            average_driving_time_min /= len(self._users)
            average_driving_distance_m /= len(self._users)

            if population > max_dict["pop"]:
                max_dict["pop"] = population
            if average_distance> max_dict["hav"]:
                max_dict["hav"] = average_distance
            if average_driving_time_min > max_dict["time"]:
                max_dict["time"] = average_driving_time_min
            if average_driving_distance_m > max_dict["drive"]:
                max_dict["drive"] = average_driving_distance_m

            city.Set_SubScore("pop",population)
            city.Set_SubScore("hav",average_distance)
            city.Set_SubScore("time",average_driving_time_min)
            city.Set_SubScore("drive",average_driving_distance_m)

        for city in self._cities:
            for key,max_value in max_dict.items():
                if max_value > 0:
                    city.Set_NormScore(key,city.Get_SubScore(key)/max_value)
            city.Set_Score(self._Score_Function(city))
        self._valid_calculation = True

    def Get_Geographical_Center(self):
        avg_lat = 0.0
        avg_lon = 0.0
         
        for user in self._users:
            coord = user.Get_Location()
            avg_lat += coord.Get_Latitude()
            avg_lon += coord.Get_Longitude()
        
        avg_lat /= len(self._users)
        avg_lon /= len(self._users)

        return (avg_lat,avg_lon)

    # https://stackoverflow.com/questions/31696411/google-maps-directions-python
    def Get_Driving_Directions(self,city,user):
        return self._Google_Estimate_API(city,user)          

    def _Google_Directions_API(self,city,user) :
        start = city.Get_Google_API_String()
        finish = user.Get_Coordinate().Get_Google_API_String()

        url = 'http://maps.googleapis.com/maps/api/directions/json?%s' % urllib.parse.urlencode((
                    ('origin', start),
                    ('destination', finish)
        ))

        tries = 50
        got_json = False
        try_attempt = 0
        while try_attempt < tries:            
            try:
                ur = urllib.request.urlopen(url)
                result = json.load(ur)
        
                driving_distance_meters = result["routes"][0]["legs"][0]["distance"]["value"]
                travel_time_minutes = result["routes"][0]["legs"][0]["duration"]["value"] / 60.0
                return (driving_distance_meters,travel_time_minutes)
            except:
                try_attempt += 1

        raise Exception("Couldn't complete Google API Request.")      

    def _Google_Estimate_API(self,city,user) :
        start = city.Get_Google_API_String()
        finish = user.Get_Coordinate().Get_Google_API_String()

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

    def _Google_Estimate_API_Matrix(self) :

        distance_matrix = np.empty([len(self._cities),len(self._users)])
        time_matrix = np.empty([len(self._cities),len(self._users)])

        start_string = ''
        for user in self._users:
            start_string += user.Get_Location().Get_Coordinate().Get_Google_API_String() + '|'
        start_string = start_string[:-1] # ignore last bar
        
        finish_string = ''
        for city in self._cities:
            finish_string += city.Get_Coordinate().Get_Google_API_String() + '|'

        url = 'https://maps.googleapis.com/maps/api/distancematrix/json?%s' % urllib.parse.urlencode((
                    ('origins', start_string),
                    ('destinations', finish_string)
        ))

        tries = 50
        got_json = False
        try_attempt = 0
        while try_attempt < tries:            
            try:
                ur = urllib.request.urlopen(url)
                result = json.load(ur)
        
                # ["rows"][userindex]["elements"][cityindex]
                for city_index in range(len(self._cities)):
                    for user_index in range(len(self._users)):
                        distance_matrix[city_index][user_index] = result["rows"][user_index]["elements"][city_index]["distance"]["value"]
                        time_matrix[city_index][user_index] = result["rows"][user_index]["elements"][city_index]["duration"]["value"] / 60.0                
                
                return (distance_matrix,time_matrix)
            except:
                try_attempt += 1
        
        raise Exception(result["error_message"]) 

    def Plot_Results(self):
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