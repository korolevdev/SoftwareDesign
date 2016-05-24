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

    def init_date(self):
        if self.epoch_yr < 57:
            year = self.epoch_yr + 2000
        else:
            year = self.epoch_yr + 1900
        mon, day, hr, minute, sec = days2mdhms(year, self.epoch_day)
        sec_whole, sec_frac = divmod(sec, 1.0)
        self.date = datetime(year, mon, day, hr, minute, int(sec_whole),
                             int(sec_frac * 1000000.0 // 1.0), timezone.utc)
        self.timestamp = int(time.mktime(self.date.timetuple()))
        self.jdate = jday(year, mon, day, hr, minute, sec)

    def init_sgp4(self):
        xpdotp = 1440.0 / (2.0 * pi)

        self.sgp4 = sgp4model.Satellite()

        self.sgp4.error = 0
        self.sgp4.whichconst = wgs84

        self.sgp4.no = self.no / xpdotp
        self.sgp4.bstar = self.bstar * pow(10.0, self.ibexp)
        self.sgp4.a = pow(self.sgp4.no * wgs84.tumin, (-2.0 / 3.0))
        self.sgp4.inclo = radians(self.inclo)
        self.sgp4.nodeo = radians(self.nodeo)
        self.sgp4.argpo = radians(self.argpo)
        self.sgp4.mo = radians(self.mo)
        self.sgp4.alta = self.sgp4.a * (1.0 + self.ecco) - 1.0
        self.sgp4.altp = self.sgp4.a * (1.0 - self.ecco) - 1.0

        self.sgp4.epochyr = self.date.year
        self.sgp4.jdsatepoch = self.jdate
        self.sgp4.epoch = self.date
        self.sgp4.ecco = self.ecco
        propagation.sgp4init(
            wgs84, 'i', self.norad, self.sgp4.jdsatepoch - 2433281.5,
            self.sgp4.bstar, self.sgp4.ecco, self.sgp4.argpo, self.sgp4.inclo,
            self.sgp4.mo, self.sgp4.no, self.sgp4.nodeo, self.sgp4
        )

        self.init = True


class Sat:

    def __init__(self, orbdata=None):
        self.name = "unnamed"
        self.classified = False
        self.year = 0
        self.norad = 0
        self.intl = "00000A"
        self.country = "N/A"
        self.orbdata = OrbitData() if orbdata is None else orbdata

    def __str__(self):
        return "sat #{} ({}/{}) last {}".format(
            self.norad, 
            self.name, 
            self.intl, 
            self.orbdata.date
        )

    def __repr__(self):
        return self.__str__()