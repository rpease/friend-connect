from multipledispatch import dispatch
from math import *
import typing

EARTH_RADIUS_KM = 6.3781e3
DEGREES_PER_RADIAN = 180.0 / pi
RADIANS_PER_DEGREE = 1.0 / DEGREES_PER_RADIAN
MILES_PER_KILOMETER = 0.621371 / 1.0


def Convert_Geo_To_Spherical(latitude: float, longitude: float) -> tuple:
    """Converts a latitude and longitude to spherical coordinates.
    
    Arguments:
        latitude {float} -- latitude [degrees]
        longitude {float} -- longitude [degrees]
    
    Returns:
        tuple -- (radius [km],polar angle [radians], azimuthal angle [radians])
    """

    r = EARTH_RADIUS_KM

    polar_angle_degrees = 90.0 - latitude
    polar_angle_radians = RADIANS_PER_DEGREE * polar_angle_degrees

    azimuthal_angle_degrees = longitude
    azimuthal_angle_radians = RADIANS_PER_DEGREE * azimuthal_angle_degrees

    return r, polar_angle_radians, azimuthal_angle_radians


def Convert_Spherical_To_Geo(r: float, polar_angle_radians: float, azimuthal_angle_radians: float) -> tuple:
    """Converts spherical coordinates into a latitude and longitude
    
    Arguments:
        r {float} -- radius [km]
        polar_angle_radians {float} -- polar angle [radians]
        azimuthal_angle_radians {float} -- azimuthal angle [radians]
    
    Raises:
        ValueError -- Throws error if radius is not close to Earth'r radius
    
    Returns:
        tuple -- (latitude [degrees], longitude [degrees])
    """

    radius_percent_error = abs(r - EARTH_RADIUS_KM) / EARTH_RADIUS_KM
    if radius_percent_error > 0.003:
        print("Provided Spherical Coordinate not valid for a geological position.")
        print(f"r = {r}")
        print(f"Earth's Radius [km] = {EARTH_RADIUS_KM}")
        raise ValueError

    polar_angle_degrees = DEGREES_PER_RADIAN * polar_angle_radians
    latitude = 90.0 - polar_angle_degrees

    azimuthal_angle_degrees = DEGREES_PER_RADIAN * azimuthal_angle_radians
    longitude = azimuthal_angle_degrees

    return latitude, longitude


def hav(angle_radians: float) -> float:
    """Calculates the haversine function for the specified degrees.
    
    Arguments:
        angle_radians {float} -- angle [radians]
    
    Returns:
        float -- the result of the haversine function
    """

    return (1.0 - cos(angle_radians)) / 2.0


@dispatch(float, float, float, float)
def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the haversine distance between the two provided coordinates.
    
    Arguments:
        lat1 {float} -- latitude of coordinate 1 [degrees]
        lon1 {float} -- longitude of coordinate 1 [degrees]
        lat2 {float} -- latitude of coordinate 2 [degrees]
        lon2 {float} -- longitude of coordinate 2 [degrees]
    
    Returns:
        float -- The haversine distance between the two coordinates [km]
    """

    r1, polar1, azi1 = Convert_Geo_To_Spherical(lat1, lon1)
    _, polar2, azi2 = Convert_Geo_To_Spherical(lat2, lon2)

    term1 = hav(polar1 - polar2)
    term2 = cos(polar1) * cos(polar2)
    term3 = hav(azi1 - azi2)
    sqrt_term = sqrt(term1 + term2 * term3)
    return 2.0 * r1 * asin(sqrt_term)


@dispatch(tuple, tuple)
def haversine_distance_km(coordinate1: tuple, coordinate2: tuple) -> float:
    """Calculates the haversine distance between the two provided coordinates.
   
    Arguments:
        coordinate1 {tuple} -- (latitude,longitude)
        coordinate2 {tuple} -- (latitude,longitude)
    
    Returns:
        float -- The haversine distance between the two coordinates [km]
    """
    return haversine_distance_km(coordinate1[0], coordinate1[1], coordinate2[0], coordinate2[1])
