from multipledispatch import dispatch
from Location import *
import typying

class User:

	_name: str
	_user_id: int
	_location: GeoLocation	

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

    @dispatch(GeoLocation)
    def set_location(self,location: GeoLocation):
        self._location = location
		self._location.set_name(self._name)

    @dispatch(float,float)
    def set_location(self,latitude: float,longitude: float):
        self._location = GeoLocation(self._name,latitude,longitude)

    def get_location(self)-> GeoLocation:
        return self._location
		
	def get_ID(self)-> int:
		return self._user_id
		
	def get_name(self)-> str:
		return self._name
		