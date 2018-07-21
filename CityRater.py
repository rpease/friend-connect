from multipledispatch import dispatch
from Friend import *

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