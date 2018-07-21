from multipledispatch import dispatch
import math

EARTH_RADIUS_KM = 6.3781e3
DEGREES_PER_RADIAN = 180.0 / math.pi
RADIANS_PER_DEGREE = 1.0 / DEGREES_PER_RADIAN

def Convert_Geo_To_Spherical(latitude,longitude):

    r = EARTH_RADIUS_KM
    
    polar_angle_degrees = 90.0 - latitude
    polar_angle_radians = RADIANS_PER_DEGREE * polar_angle_degrees

    azimuthal_angle_degrees = longitude
    azimuthal_angle_radians = RADIANS_PER_DEGREE * azimuthal_angle_degrees

    return (r,polar_angle_radians,azimuthal_angle_radians)

def Convert_Spherical_To_Geo(r,polar_angle_radians,azimuthal_angle_radians):

    radius_percent_error = abs(r-EARTH_RADIUS_KM) / EARTH_RADIUS_KM
    if radius_percent_error > 0.003:
        print("Provided Spherical Coordinate not valid for a geological position.")
        print("r = {r}")
        print("Earth's Radius [km] = {EARTH_RADIUS_KM}")

    polar_angle_degrees = DEGREES_PER_RADIAN * polar_angle_radians
    latitude = 90.0 - polar_angle_degrees

    azimuthal_angle_degrees = DEGREES_PER_RADIAN * azimuthal_angle_radians
    longitude = azimuthal_angle_degrees

    return (latitude,longitude)

def hav(angle_radians):
    return (1.0-math.cos(angle_radians))/2.0
