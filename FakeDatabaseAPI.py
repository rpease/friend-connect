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
    _metric_table: dict
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
        self._metric_table = {}

    def load_city_table(self, city_file_path: str):
        """

        :param city_file_path: csv file containing city data
        :return:
        """

        df = pd.read_csv(city_file_path, encoding='iso-8859-1', index_col="name")  # required encoding for this file
        self._city_table = df[(df["country code"] == "CA") | (df["country code"] == "US") | (df["country code"] == "MX")]
        self._city_table["latitude"] = self._city_table["latitude"].astype(float)
        self._city_table["longitude"] = self._city_table["longitude"].astype(float)
        self._city_table["population"] = self._city_table["population"].astype(float)
        self._city_table = self._city_table.sort_values(by=['population'],ascending=False)
        self._city_table = self._city_table.iloc[:200]

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

    def get_destination_coordinate(self,name: str)->tuple:
        print(name)
        lat = float(self._city_table.loc[name,"latitude"])
        lon = float(self._city_table.loc[name,"longitude"])
        return (lat,lon)

    def get_user_destination_distance_matrix(self, session_id: int) ->dict:
        """
        Calculates the distances between every user and every destination
        :return: json string
        """
        dict_matrix = {}

        for city_name,city in self._city_table.iterrows():            
            c_lat = city["latitude"]
            c_lon = city["longitude"]
            dict_matrix[city_name] = {}

            for u,user in self._users_table.iterrows():
                name = user["Name"]                
                u_lat = user["Latitude"]
                u_lon = user["Longitude"]            
                
                distance_km = GeoUtilities.haversine_distance_km(u_lat,u_lon,c_lat,c_lon)                
                dict_matrix[city_name][name] = distance_km

        return dict_matrix

    def get_user_destination_distance_matrix_json(self, session_id: int) ->str:
        """
        Calculates the distances between every user and every destination
        :return: json string
        """
        return json.dumps(self.get_user_destination_distance_matrix(session_id))

    def get_user_destination_driving_matrix(self, session_id: int)->dict:
        """
        Calculates the distances and times between every user and every destination
        :return: json string
        """
        print("Using haversine distance as an approximation.")

        dict_matrix = {}

        driving_speed_kmh = 112.65

        for city_name,city in self._city_table.iterrows():            
            c_lat = city["latitude"]
            c_lon = city["longitude"]
            dict_matrix[city_name] = {}

            for u,user in self._users_table.iterrows():
                name = user["Name"]                
                u_lat = user["Latitude"]
                u_lon = user["Longitude"]            
                
                distance_km = GeoUtilities.haversine_distance_km(u_lat,u_lon,c_lat,c_lon)
                dict_matrix[city_name][name] = {}
                dict_matrix[city_name][name]["Distance [km]"] = distance_km
                dict_matrix[city_name][name]["Time [hr]"] = distance_km/driving_speed_kmh

        return dict_matrix

    def get_user_destination_driving_matrix_json(self, session_id: int)->str:
        """
        Calculates the distances and times between every user and every destination
        :return: json string
        """
        return json.dumps(self.get_user_destination_driving_matrix(session_id))

    def get_user_data(self, session_id: int)->dict:
        data = {}
        for u,user in self._users_table.iterrows():
            data[user["Name"]] = {}
            data[user["Name"]]["latitude"] = user["Latitude"]
            data[user["Name"]]["longitude"] = user["Longitude"]
        return data

    def get_user_data_json(self, session_id: int)->str:
        return json.dumps(self.get_user_data(session_id))

    def get_airport_matrix(self, session_id: int)-> str:
        """
        Calculates the time and cost to fly between all major airports
        :return: json string
        """
        pass

    def _update_score_data(self,session_id: int):

        if not session_id in self._metric_table:
            self._metric_table[session_id] = {}
        
        haversine_matrix = self.get_user_destination_distance_matrix(session_id)
        driving_matrix = self.get_user_destination_driving_matrix(session_id)

        self._metric_table[session_id]["MAX"] = {}
        self._metric_table[session_id]["MIN"] = {}

        for destination,_ in haversine_matrix.items():

            if not destination in self._metric_table[session_id]:
                self._metric_table[session_id][destination] = {}                

            for u,user in self._users_table.iterrows():
                name = user["Name"]

                if not name in self._metric_table[session_id]:
                    self._metric_table[session_id][destination][name] = {}                 

                self._metric_table[session_id][destination][name]["haversine"] = haversine_matrix[destination][name]
                self._metric_table[session_id][destination][name]["drive distance"] = driving_matrix[destination][name]["Distance [km]"]
                self._metric_table[session_id][destination][name]["drive time"] = driving_matrix[destination][name]["Time [hr]"]
                self._metric_table[session_id][destination][name]["fun"] = 1.0
                self._metric_table[session_id][destination][name]["airline time"] = 1.0
                self._metric_table[session_id][destination][name]["airline cost"] = 1.0

                # Save maximum and minimum values for normalization purposes
                for metric,value in self._metric_table[session_id][destination][name].items():
                    if not metric in self._metric_table[session_id]["MAX"]:
                        self._metric_table[session_id]["MAX"][metric] = -1e6
                        self._metric_table[session_id]["MIN"][metric] = 1e6

                    if value > self._metric_table[session_id]["MAX"][metric]:
                        self._metric_table[session_id]["MAX"][metric] = value
                    if value < self._metric_table[session_id]["MIN"][metric]:
                        self._metric_table[session_id]["MIN"][metric] = value
                
    def _get_destination_scores(self,session_id: int)->dict:

        if not session_id in self._metric_table:
            print(f"Session ID {session_id} does not exist!")
            raise ValueError
        
        city_scores = {}

        session_metrics = self._metric_table[session_id]
        weights = self.get_weights(session_id)
        
        for city,city_data in session_metrics.items():

            if not city == "MAX" and not city == "MIN":                

                if city not in city_scores:
                    city_scores[city] = 0.0

                for metric,w in weights.items():
                    
                    if metric in session_metrics["MAX"]:
                        max_value = session_metrics["MAX"][metric]
                        min_value = session_metrics["MIN"][metric]
                        diff = max_value - min_value

                        if diff > 0:
                            for user,user_data in city_data.items():
                                user_metric = user_data[metric]

                                user_score = 0.0
                                if w > 0:
                                    user_score = (user_metric-min_value)/(diff)
                                elif w < 0:
                                    user_score = -(max_value-user_metric)/(diff)                                    

                                city_scores[city] += (1.0/len(city_data))*w*user_score

        return city_scores  

    def _get_destination_scores_json(self,session_id: int)->str:
        return json.dumps(self._get_destination_scores(session_id))                              

    def get_scores(self, session_id: int)-> str:
        self._update_score_data(session_id)
        scores = self._get_destination_scores(session_id)

        full_data = {}
        full_data["city_scores"] = {}
        
        max_value = -1e6
        min_value = 1e6
        for city,value in scores.items():
            lat,lon = self.get_destination_coordinate(city)

            full_data["city_scores"][city] = {}
            full_data["city_scores"][city]["score"] = value
            full_data["city_scores"][city]["latitude"] = lat
            full_data["city_scores"][city]["longitude"] = lon

            if value > max_value:
                max_value = value
            if value < min_value:
                min_value = value

        full_data["metadata"] = {}
        full_data["metadata"]["max_score"] = max_value
        full_data["metadata"]["min_score"] = min_value
        full_data["metadata"]["center"] = {}
        lat,lon = self.get_geographical_center(session_id)
        full_data["metadata"]["center"]["latitude"] = lat
        full_data["metadata"]["center"]["longitude"] = lon        

        return json.dumps(full_data)

    def get_weights(self,session_id: int)-> pd.DataFrame:
        """

        :param session_id:
        :return:
        """
        if not session_id in self._weight_table:
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

    def get_geographical_center(self, session_id: int)->str:
        
        lat_center = 0.0
        lon_center = 0.0
        num_users = 0
        for u,user in self._users_table.iterrows():

            name = user["Name"]
            lat = user["Latitude"]
            lon = user["Longitude"]

            lat_center += lat
            lon_center += lon

            num_users += 1
        
        lat_center /= num_users
        lon_center /= num_users

        return lat_center,lon_center
