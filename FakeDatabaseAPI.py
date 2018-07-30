import pandas as pd
from multipledispatch import dispatch
import User
import json

class FakeDatabaseAPI:

    _city_table: pd.DataFrame
    _park_table: pd.DataFrame
    _users_table: pd.DataFrame
    _score_table: pd.DataFrame
    _weight_table: pd.DataFrame

    @dispatch()
    def __init__(self):

    @dispatch(str)
    def __init__(self, city_file_path: str, park_file_path: str):
        self.load_city_table(city_file_path)
        self.load_park_table(park_file_path)

    def load_city_table(self, city_file_path: str):
        """

        :param city_file_path: csv file containing city data
        :return:
        """

        df = pd.read_csv(city_file_path, encoding='iso-8859-1')  # required encoding for this file
        self._city_table = df[(df["country code"] == "CA") | (df["country code"] == "US") | (df["country code"] == "MX")]

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

    def add_user(self,user: User):
        """
        Adds a new user to the database
        :param user:
        :return:
        """
        pass

    def get_user_destination_distance_matrix(self) ->str:
        """
        Calculates the distances between every user and every destination
        :return: json string
        """
        pass

    def get_user_destination_driving_matrix(self)->str:
        """
        Calculates the distances and times between every user and every destination
        :return: json string
        """
        pass

    def get_airport_matrix(self)-> str:
        """
        Calculates the time and cost to fly between all major airports
        :return: json string
        """
        pass

    def update_scores(self):
        pass

    def get_scores(self)-> str:
        pass
