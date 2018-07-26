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

    df = pandas.read_csv(file_path,encoding='iso-8859-1')
    df = df[df["population"] > 10000.0]
    df = df[(df["country code"] == "CA" )| (df["country code"] == "US") | (df["country code"] == "MX")]
    df = df.sort_values(by=['population'],ascending=False)
    df = df.iloc[:400]

    for index,row in df.iterrows():        
        new_city = City(row["name"],row["latitude"],row["longitude"])
        new_city.Set_Population(row["population"])
        cities.append(new_city)       

    print(f"Loaded {len(cities)} cities")
    return cities    

test_users = LoadFakeUsers(r"test_data\users.csv")
test_cities = LoadCities(r"test_data\city15000.csv")

city_rater = CityRater(test_cities,test_users)
city_rater.Set_Population_Weight(1.0)
top_cities = city_rater.Get_Top_Cities()

for city in top_cities:
    print(city)

city_rater.Plot_Results()