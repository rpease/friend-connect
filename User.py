from multipledispatch import dispatch
from Location import *
import typing

class User:

    _name: str
    _user_id: int
    _location: GeoCoordinate
    _static_user_id = 0

    @dispatch(str)
    def __init__(self,name: str):
        self._name = name
        User._static_user_id += 1
        self._user_id = User._static_user_id

    @dispatch(str,float,float)
    def __init__(self,name: str,latitude: float,longitude: float):
        self.__init__(name)
        self.set_location(latitude,longitude)

    def __str__(self):
        out_string = f"{self._user_id}\t{self._name}"
        return out_string

    @dispatch(GeoCoordinate)
    def set_location(self,location: GeoCoordinate):
        self._location = location

    @dispatch(float,float)
    def set_location(self,latitude: float,longitude: float):
        self._location = GeoCoordinate(latitude,longitude)

    def get_location(self)-> GeoCoordinate:
        return self._location

    def get_ID(self)-> int:
        return self._user_id

    def get_name(self)-> str:
        return self._name
