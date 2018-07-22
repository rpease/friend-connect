from GeoUtilities import *
from math import *
from multipledispatch import dispatch

class GeoCoordinate:

    def __init__(self,latitude,longitude):
        if latitude > 90.0 or latitude < -90:
            print("Provided latitude not valid")
            print("-90 <= Latitude <= 90")
            print("Provided latitude = {latitude}")
        if longitude > 180.0 or longitude < -180.0:
            print("Provided longitude not valid")
            print("-180.0 <= Longitude <= 180.0")
            print("Provided latitude = {longitude}")

        self.latitude = latitude
        self.longitude = longitude

        self._r, self._polar_angle, self._azimuthal_angle = Convert_Geo_To_Spherical(latitude,longitude)

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

    @dispatch(float,float)
    def Get_Distance_Km(self,lat,lon):

        r,polar,azi = Convert_Geo_To_Spherical(lat,lon)

        term1 = hav(polar - self._polar_angle)
        term2 = cos(polar)*cos(self._polar_angle)
        term3 = hav(azi - self._azimuthal_angle)
        sqrt_term = math.sqrt(term1 + term2*term3)
        return 2.0*self._r*math.asin(sqrt_term)

    def Get_Google_API_String(self):
        return f"{self.latitude},{self.longitude}"

class GeoLocation:

    def __init__(self,name,latitude = 0.0,longitude = 0.0):
        self._name = name
        self._coordinate = GeoCoordinate(latitude,longitude)

    def Get_Name(self):
        return self._name
    
    def Get_Coordinate(self):
        return self._coordinate

    def Get_Latitude(self):
        return self._coordinate.latitude

    def Get_Longitude(self):
        return self._coordinate.longitude

    def Get_Distance_Km(self,friend):
        coord = friend.Get_Location()
        other_lat = coord.Get_Latitude()
        other_lon = coord.Get_Longitude()
        return self._coordinate.Get_Distance_Km(other_lat,other_lon)

    def __str__(self):
        return f"{self._name}:\t{self._coordinate}"

class City(GeoLocation):

    def __init__(self,name,latitude,longitude):
        super().__init__(name,latitude,longitude)
        self._sub_scores = {}
        self._norm_scores = {}

    def Set_Population(self,population):
        self._population = population

    def Get_Population(self):
        return self._population

    def Set_Score(self,score):
        self._score = score

    def Get_Score(self):
        return self._score

    def Set_SubScore(self,key,value):           
        self._sub_scores[key] = value

    def Get_SubScores(self):
        return self._sub_scores
    
    def Get_SubScore(self,key):
        return self._sub_scores[key]

    def Get_NormScore(self,key):
        if key in self._norm_scores:
            return self._norm_scores[key]
        else:
            return 0.0
    
    def Set_NormScore(self,key,value):
        self._norm_scores[key] = value
    
    def __lt__(self,other):
        if self._score < other.Get_Score():
            return True
        else:
            return False

    def __gt__(self,other):
        return not self.__lt__(self,other)

    def __str__(self):
        return f"{self._score}\t{self._name}:\t{self._coordinate}"

    def Get_Description(self):
        #outstring = f"{self._name}\n"
        outstring = "Average Absolute Distance = {:.0f} miles\n".format(self._sub_scores["hav"]*MILES_PER_KILOMETER)
        #outstring+= "Population = {:,}\n".format(self._sub_scores["pop"])
        #outstring+= "Average Drive Distance = {:,} [km]\n".format(self._sub_scores["drive"]/1000.0)
        outstring+= "Average Drive Time = {:.1f} hours\n".format(self._sub_scores["time"]/60.0)

        return outstring