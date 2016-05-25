from decoder import DecoderGeneric, EncodedValueError
from sgp import Sat, OrbitData
from utils import tle_checksum
import os


class TLEDecoder(DecoderGeneric):
    fmt = "tle"
    err_tle_linenum = "invalid number of lines (expected 2 or 3)"
    err_tle_lineone = "invalid line 1 format"
    err_tle_linetwo = "invalid line 2 format"
    err_tle_linechk = "invalid line checksum"

    def __init__(self):
        self.cline = 0

    def sat_from_tle(self, lines):
        name = ""
        if len(lines) == 3:
            name = lines.pop(0).rstrip()
            self.cline += 1
        elif len(lines) != 2:
            raise EncodedValueError(
                self.fmt, TLEDecoder.err_tle_linenum, "line %s" % self.cline
            )

        sat = Sat()
        chk = 0

        line = lines.pop(0).rstrip()
        self.cline += 1
        try:
            assert line.startswith('1 ')
            sat.norad = int(line[2:7])
            assert line[8] == ' '
            sat.intl = line[9:17].rstrip()
            assert line[17] == ' '
            sat.orbdata.epoch_yr = int(line[18:20])
            assert line[23] == '.'
            sat.orbdata.epoch_day = float(line[20:32])
            assert line[32] == ' '
            assert line[34] == '.'
            sat.orbdata.ndot = float(line[33:43])
            assert line[43] == ' '
            sat.orbdata.nddot = float(line[44] + '.' + line[45:50])
            sat.orbdata.nexp = int(line[50:52])
            assert line[52] == ' '
            sat.orbdata.bstar = float(line[53] + '.' + line[54:59])
            sat.orbdata.ibexp = int(line[59:61])
            assert line[61] == ' '
            assert line[63] == ' '
            chk = int(line[-1])
        except (AssertionError, IndexError, ValueError):
            raise EncodedValueError(
                self.fmt, TLEDecoder.err_tle_lineone, "line %s" % self.cline
            )
        if chk != tle_checksum(line[:-1]):
            raise EncodedValueError(
                self.fmt, TLEDecoder.err_tle_linechk, "line %s" % self.cline
            )
        
        line = lines.pop(0).rstrip()
        self.cline += 1
        try:
            assert line.startswith('2 ')
            tnorad = int(line[2:7])
            assert tnorad == sat.norad
            assert line[7] == ' '
            assert line[11] == '.'
            sat.orbdata.inclo = float(line[8:16])
            assert line[16] == ' '
            assert line[20] == '.'
            sat.orbdata.nodeo = float(line[17:25])
            assert line[25] == ' '
            sat.orbdata.ecco = float('0.' + line[26:33].replace(' ', '0'))
            assert line[33] == ' '
            assert line[37] == '.'
            sat.orbdata.argpo = float(line[34:42])
            assert line[42] == ' '
            assert line[46] == '.'
            sat.orbdata.mo = float(line[43:51])
            assert line[51] == ' '
            sat.orbdata.no = float(line[52:63])
            sat.orbdata.revnum = int(line[63:68])
            chk = int(line[-1])
        except (AssertionError, IndexError, ValueError):
            raise EncodedValueError(
                self.fmt, TLEDecoder.err_tle_linetwo, "line %d" % self.cline
            ) 
        if chk != tle_checksum(line[:-1]):
            raise EncodedValueError(
                self.fmt, TLEDecoder.err_tle_linechk, "line %d" % self.cline
            )

        sat.orbdata.init_date()

        if name == "":
            sat.name = sat.intl
        else:
            sat.name = name

        return sat

    def decode(self, str):
        self.cline = 0
        lines = self.str.splitlines()
        return [self.sat_from_tle(self, lines)]


class TLEListDecoder(TLEDecoder):
    fmt = "tlelist"
    err_tle_list = "invalid TLE list"

    def decode(self, str):
        sats = []
        lines = []
        self.cline = 0

        for ln in str.splitlines():
            ln = ln.strip()
            if ln == "":
                self.cline += 1
                continue
            lines.append(ln)
            if len(lines) == 3:
                sats.append(self.sat_from_tle(lines))
                lines = []

        if not sats:
            if lines:
                sats.append(self.sat_from_tle(lines))
            else:
                raise EncodedValueError(self.fmt, TLEListDecoder.err_tle_list)

        return sats
