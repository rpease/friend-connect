from multipledispatch import dispatch
from Location import *

class Friend:

    _static_user_id = 0
    @dispatch(str)
    def __init__(self,name):
        self._name = name
        Friend._static_user_id += 1
        self._user_id = Friend._static_user_id

    @dispatch(str,float,float)
    def __init__(self,name,latitude,longitude):
        self.__init__(name)
        self.Set_Location(latitude,longitude)

    def __str__(self):
        out_string = f"Name = {self._name}\t"
        out_string += f"ID = {self._user_id}"
        return out_string

    @dispatch(GeoLocation)
    def Set_Location(self,location):
        self._location = location

    @dispatch(float,float)
    def Set_Location(self,latitude,longitude):
        self._location = GeoLocation(self._name,latitude,longitude)

    @dispatch(str,float,float)
    def Set_Location(self,name,latitude,longitude):
        self._location = GeoLocation(name,latitude,longitude)