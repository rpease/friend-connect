from Friend import *
from Location import *
from CityRater import *
import pandas

def LoadFakeUsers(file_path):
    friends = []
    df = pandas.read_csv(file_path)
    df["Name"] = df["Name"].astype(str)
    df["Latitude"] = df["Latitude"].astype(float)
    df["Longitude"] = df["Longitude"].astype(float)

    for index,row in df.iterrows():        
        new_friend = Friend(row["Name"],row["Latitude"],row["Longitude"])
        friends.append(new_friend)

    print(f"Loaded {len(friends)} users")
    return friends

def LoadCities(file_path):
    cities = []

    df = pandas.read_csv(file_path)
    df = df[df["population"] > 50000.0]

    for index,row in df.iterrows():        
        new_city = City(row["city"],row["lat"],row["lng"])
        new_city.Set_Population(row["population"])
        cities.append(new_city)       

    print(f"Loaded {len(cities)} cities")
    return cities    

test_users = LoadFakeUsers(r"test_data\users.csv")
test_cities = LoadCities(r"test_data\uscitiesv1.4.csv")

city_rater = CityRater(test_cities,test_users)
city_rater.Set_Population_Weight(0.00005)
top_cities = city_rater.Get_Top_Cities()

for city in top_cities:
    print(city)

#city_rater.Plot_Results()
city_rater.Plot_Results_Folium()
#city_rater.Plot_Results_Smopy()