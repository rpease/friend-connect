import pandas as pd
from multipledispatch import dispatch
import User
import json
import GeoUtilities

class FakeDatabaseAPI:

    _city_table: pd.DataFrame
    _park_table: pd.DataFrame
    _users_table: pd.DataFrame
    _score_table: dict
    _weight_table: dict

    @dispatch()
    def __init__(self):
        pass

    @dispatch(str,str)
    def __init__(self, city_file_path: str, park_file_path: str):
        self.load_city_table(city_file_path)
        self.load_park_table(park_file_path)
        self._score_table = {}
        self._users_table = {}

    def load_city_table(self, city_file_path: str):
        """

        :param city_file_path: csv file containing city data
        :return:
        """

        df = pd.read_csv(city_file_path, encoding='iso-8859-1')  # required encoding for this file
        self._city_table = df[(df["country code"] == "CA") | (df["country code"] == "US") | (df["country code"] == "MX")]
        self._city_table = self._city_table.sort_values(by=['population'],ascending=False)
        self._city_table = self._city_table.iloc[:10]

    def load_park_table(self, park_file_path: str):
        """

        :param park_file_path: csv file containing park data
        :return:
        """

        pass

    def load_users_table(self, user_file_path: str):
        """

        :param user_file_path: file containing csv user data
        :return:
        """

        self._users_table = pd.read_csv(user_file_path)
        self._users_table["Name"] = self._users_table["Name"].astype(str)
        self._users_table["Latitude"] = self._users_table["Latitude"].astype(float)
        self._users_table["Longitude"] = self._users_table["Longitude"].astype(float)
        
    def load_weight_table(self, file_path: str):
        """

        :param file_path: file containing csv weight data
        :return:
        """
        weight_df = pd.read_csv(file_path)
        weight_df = weight_df.set_index("session_id")
        self._weight_table = weight_df.to_dict("index")

    def add_user(self,user: User):
        """
        Adds a new user to the database
        :param user:
        :return:
        """

        if not (self._users_table["Name"] == user.get_name()).any():
            self._users_table.append({"Name": user.get_name(), "Latitude": user.get_location().latitude, "Longitude": user.get_location().longitude}, ignore_index=True)

        pass

    def get_user_destination_distance_matrix(self, session_id: int) ->dict:
        """
        Calculates the distances between every user and every destination
        :return: json string
        """
        dict_matrix = {}

        for u,user in self._users_table.iterrows():
            name = user["Name"]
            dict_matrix[name] = {}
            u_lat = user["Latitude"]
            u_lon = user["Longitude"]

            for c,city in self._city_table.iterrows():
                city_name = city["name"]
                c_lat = city["latitude"]
                c_lon = city["longitude"]
                
                distance_km = GeoUtilities.haversine_distance_km(u_lat,u_lon,c_lat,c_lon)
                
                dict_matrix[name][city_name] = distance_km

        return dict_matrix

    def get_user_destination_distance_matrix_json(self, session_id: int) ->str:
        """
        Calculates the distances between every user and every destination
        :return: json string
        """
        return json.dumps(self.get_user_destination_distance_matrix(session_id))

    def get_user_destination_driving_matrix(self, session_id: int)->str:
        """
        Calculates the distances and times between every user and every destination
        :return: json string
        """
        print("Using haversine distance as an approximation.")

        dict_matrix = {}

        driving_speed_kmh = 112.65

        for u,user in self._users_table.iterrows():
            name = user["Name"]
            dict_matrix[name] = {}
            u_lat = user["Latitude"]
            u_lon = user["Longitude"]

            for c,city in self._city_table.iterrows():
                city_name = city["name"]
                c_lat = city["latitude"]
                c_lon = city["longitude"]
                
                distance_km = GeoUtilities.haversine_distance_km(u_lat,u_lon,c_lat,c_lon)
                dict_matrix[name][city_name] = {}
                dict_matrix[name][city_name]["Distance [km]"] = distance_km
                dict_matrix[name][city_name]["Time [hr]"] = distance_km/driving_speed_kmh

        return dict_matrix

    def get_user_destination_driving_matrix_json(self, session_id: int)->str:
        """
        Calculates the distances and times between every user and every destination
        :return: json string
        """
        return json.dumps(self.get_user_destination_driving_matrix(session_id))

    def get_airport_matrix(self, session_id: int)-> str:
        """
        Calculates the time and cost to fly between all major airports
        :return: json string
        """
        pass

    def update_score_data(self,session_id: int):

        if not session_id in self._score_table:
            self._score_table[session_id] = {}
        
        haversine_matrix = self.get_user_destination_distance_matrix(session_id)
        driving_matrix = self.get_user_destination_driving_matrix(session_id)

        for u,user in self._users_table.iterrows():
            name = user["Name"]

            if not name in self._score_table[session_id]:
                self._score_table[session_id][name] = {}   

            for destination,_ in haversine_matrix[name].items():

                if not destination in self._score_table[session_id][name]:
                    self._score_table[session_id][name][destination] = {}

                self._score_table[session_id][name][destination]["haversine"] = haversine_matrix[name][destination]
                self._score_table[session_id][name][destination]["drive distance"] = driving_matrix[name][destination]["Distance [km]"]
                self._score_table[session_id][name][destination]["drive time"] = driving_matrix[name][destination]["Time [hr]"]
                self._score_table[session_id][name][destination]["fun"] = 1.0
                self._score_table[session_id][name][destination]["airline time"] = 1.0
                self._score_table[session_id][name][destination]["airline cost"] = 1.0

    def get_scores(self, session_id: int)-> str:
        self.update_score_data(session_id)
        return json.dumps(self._score_table)

    def get_weights(self,session_id: int)-> pd.DataFrame:
        """

        :param session_id:
        :return:
        """

        return self._weight_table
        if not self._weight_table.has_key(session_id):
            return {}
        else:
            return self._weight_table[session_id]

    def set_weight(self, session_id: int, key: str, new_value: float):
        """

        :param session_id:
        :param key:
        :param new_value:
        :return:
        """

        if not (self._weight_table.has_key(session_id)):
            self._weight_table[session_id] = {"fun":1.0, "haversine": 1.0,"drive_distance": 1.0,"drive_time": 1.0}
        self._weight_table[session_id][key] = new_value
