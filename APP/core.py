from dbcontroller import DBController, DBError
from renderer import Renderer
from gui_qt import QtGUIController
from decoder import DecoderError
from tledecoder import TLEListDecoder
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

    def reload_sats(self):
        try:
            self.sats = self.dbc.get_all()
        except DBError as e:
            self.gui.show_error(SatView.err_db_load.format(str(e)))
            return

        self.gui.clear_sats()
        self.gui.update()
        self.gui.set_sats(self.sats)

    def sat_by_norad(self, n):
        for s in self.sats:
            if s.norad == n:
                return s
        return None

    def save_tle(self, nums, fname):
        try:
            with open(fname, "w") as f:
                for n in nums:
                    sat = self.sat_by_norad(n)
                    if sat is None:
                        continue
                    l0 = sat.name
                    l1, l2 = sat.orbdata.get_tle(sat)
                    f.write(l0 + '\n' + l1 + '\n' + l2 + '\n')
        except EnvironmentError as e:
            self.gui.show_error(SatView.err_save.format(fname, str(e)))
            return

    def load_tle(self, fname):
        dec = TLEListDecoder()

        txt = ""
        try:
            with open(fname, "r") as f:
                txt = f.read()
        except EnvironmentError as e:
            self.gui.show_error(SatView.err_load.format(fname, str(e)))
            return

        sats = []
        try:
            sats = dec.decode(txt)
        except DecoderError as e:
            self.gui.show_error(SatView.err_decode.format(fname, str(e)))
            return

        try:
            for sat in sats:
                self.dbc.add(sat)
            self.dbc.sync()
        except DBError as e:
            self.gui.show_error(SatView.err_db_save.format(str(e)))
        finally:
            self.reload_sats()

    def run(self):
        while True:
            self.gui.update()
            for ev in self.gui.poll_events():
                ev.process(self)
            sleep(0.001)
