from multipledispatch import dispatch
from Friend import *
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import branca
import numpy as np
import webbrowser
import os

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

    def _Score_Function(self,population,distance):
        return self._weights["pop"]*population - self._weights["hav"]*distance

    def _Calculate_Scores(self):        
        for city in self._cities:   

            population = city.Get_Population()
            average_distance = 0.0

            for user in self._users:
                average_distance += city.Get_Distance_Km(user)
            average_distance /= len(self._users)

            city.Set_Score(self._Score_Function(population,average_distance))    

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

        for user in self._users:
            coord = user.Get_Location()
            x_data_user.append(coord.Get_Longitude())
            y_data_user.append(coord.Get_Latitude())

        plt.scatter(x_data,y_data,c=f_data,alpha=0.5)
        plt.colorbar()
        sns.scatterplot(x_data_user,y_data_user)        
        plt.show()     

    def Plot_Results_Folium(self):
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
                fill_color=color_code).add_to(folium_map)

        # Add users to map
        for i in range(len(y_data_user)):
            folium.Marker(location=[y_data_user[i],x_data_user[i]],
                popup=self._users[i]._name).add_to(folium_map) 

        # Heat Map
        #HeatMap(xyf_data).add_to(folium_map)

        folium_map.save("Map.html")
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("Map.html",new=1)
        os.remove("Map.html")