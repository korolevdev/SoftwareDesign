from math import pi, radians
from datetime import datetime, timezone
from sgp4 import model as sgp4model
from sgp4.earth_gravity import wgs84
from sgp4.ext import jday, days2mdhms
from sgp4 import propagation
from utils import tle_checksum
import time


class OrbitData:

    def __init__(self):
        self.init = False


class Sat:

    def __init__(self, orbdata=None):
        self.name = "unnamed"
        self.classified = False
        self.year = 0
        self.norad = 0
        self.intl = "00000A"
        self.country = "N/A"
        self.orbdata = OrbitData() if orbdata is None else orbdata