from math import fmod, sqrt, atan2, sin, degrees, pi, log, tan
from utils import jt_to_gmst


def wgs84_to_lonlat(x, y, z, gmst):
    a = 6378.137
    b = 6356.7523142
    r = sqrt(x * x + y * y)
    f = (a - b) / a
    e2 = 2 * f - f * f

    lon = atan2(y, x) - gmst
    lat = atan2(z, r)

    for i in range(0, 20):
        sl = sin(lat)
        c = 1 / sqrt(1 - e2 * sl * sl)
        lat = atan2(z + a * c * e2 * sl, r)

    return lon, lat



def normalize_lon(lon):
    x = fmod(lon + pi, 2 * pi)
    if x < 0:
        x += 2 * pi

    return x - pi