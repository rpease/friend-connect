from Friend import *
from Location import *
import pandas
from urllib.request import urlretrieve

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
    df = df[df["population"] > 1000.0]

    for index,row in df.iterrows():        
        new_city = GeoLocation(row["city"],row["lat"],row["lng"])
        cities.append(new_city)       

    print(f"Loaded {len(cities)} cities")
    return cities    

test_users = LoadFakeUsers(r"test_data\users.csv")
test_cities = LoadCities(r"test_data\uscitiesv1.4.csv")

