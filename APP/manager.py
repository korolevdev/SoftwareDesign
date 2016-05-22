from database import DBController, DBError
from renderer import Renderer
from gui_qt import QtGUIController
from decoder import DecoderError
from tle_decoder import TLEListDecoder
from time import sleep
import os


class SatView:
    err_db_load = "Could not get sats from database:\n{}"
    err_db_save = "Could not insert sats into database:\n{}"
    err_save = "Could not load TLE from {}:\n{}"
    err_load = "Could not save TLE to {}:\n{}"
    err_decode = "Could not decode TLE in {}:\n{}"

    def __init__(self):
        self.dbc = DBController()
        self.rdr = Renderer()
        self.gui = QtGUIController()
        self.sats = []
        self.reload_sats()