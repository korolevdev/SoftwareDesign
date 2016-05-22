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


class TLEListDecoder(TLEDecoder):
    fmt = "tlelist"
    err_tle_list = "invalid TLE list"
