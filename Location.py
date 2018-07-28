from GeoUtilities import *
from math import *
from multipledispatch import dispatch
import typing


class GeoCoordinate:

    latitude: float
    longitude: float
    _r: float
    _polar_angle: float
    _azimuthal_angle: float

    def __init__(self, lat: float, lon: float):
        if lat > 90.0 or lat < -90:
            error_string = f"Provided latitude not valid\n-90 <= Latitude <= 90\nProvided: {latitude}"
            raise ValueError(error_string)
        if lon > 180.0 or lon < -180.0:
            error_string = f"Provided longitude not valid\n-180 <= Latitude <= 180\nProvided: {longitude}"
            raise ValueError(error_string)

        self.latitude = lat
        self.longitude = lon

        self._r, self._polar_angle, self._azimuthal_angle = Convert_Geo_To_Spherical(lat, lon)

    def __str__(self):
        out_lat = f"{self.latitude}N"
        if self.latitude < 0:
            neg_lat = -self.latitude
            out_lat = f"{neg_lat}S"

        out_lon = f"{self.longitude}E"
        if self.latitude < 0:
            neg_lon = -self.longitude
            out_lon = f"{neg_lon}W"

        return f"({out_lat},{out_lon})"

    @dispatch(float, float)
    def get_distance_km(self, lat: float, lon: float)-> float:
        return haversine_distance_km(self.latitude, self.longitude, lat, lon)

    @dispatch(float, tuple)
    def get_distance_km(self, coordinate: tuple)-> float:
        return haversine_distance_km(self.latitude, self.longitude, coordinate[0], coordinate[1])

    def get_google_api_string(self)-> str:
        return f"{self.latitude},{self.longitude}"


class VacationDestination:

    _name: str
    _coordinate: GeoCoordinate

    def __init__(self, name: str, latitude=0.0, longitude=0.0):
        self.set_name(name)
        self.set_location(latitude, longitude)

    def set_location(self, lat: float, lon: float):
        self._coordinate = GeoCoordinate(lat, lon)

    def set_name(self, name: str):
        self._name = name

    def get_name(self)-> str:
        return self._name

    def get_location(self)-> GeoCoordinate:
        return self._coordinate

    def get_latitude(self)-> float:
        return self._coordinate.latitude

    def get_longitude(self)-> float:
        return self._coordinate.longitude

    @dispatch(GeoCoordinate)
    def get_distance_km(self, coordinate: GeoCoordinate)-> float:
        return self.get_distance_km(coordinate.latitude, coordinate.longitude)

    @dispatch(float, float)
    def get_distance_km(self, lat: float, lon: float)-> float:
        return self._coordinate.get_distance_km(lat, lon)

    def get_fun_score(self)-> float:
        raise NotImplementedError("Fun score not implemented")

    def get_outdoor_score(self)-> float:
        raise NotImplementedError("Outdoor score not implemented")

    def get_description(self)-> str:
        return f"{self._name}:\t{self._coordinate}"

    def __str__(self):
        return self.get_description()


class City(VacationDestination):

    _population: float

    def __init__(self, name: str, latitude: float, longitude: float, pop: float):
        self.set_name(name)
        self.set_location(latitude, longitude)
        self.set_population(pop)

    def set_population(self,pop: float):
        if pop <= 0:
            raise ValueError(f"Population must be greater than 0\nProvided: {pop}")
        self._population = pop

    def get_population(self)-> float:
        return self._population

    def get_fun_score(self)-> float:
        return self.get_population()

    def get_outdoor_score(self)-> float:
        return 0.0

    def get_description(self)-> str:
        return f"{self._name}:\t{self._population}\t{self._coordinate}"


class Park(VacationDestination):

    _park_area_km2: float

    def set_park_area(self, area: float):
        if area <= 0:
            raise ValueError(f"Park Area must be greater than 0\nProvided: {pop}")
        self._park_area_km2 = area

    def get_fun_score(self)-> float:
        return self._park_area_km2

    def get_outdoor_score(self)-> float:
        return 1.0

    def get_description(self)-> str:
        return f"{self._name}:\t{self._park_area_km2}\t{self._coordinate}"
