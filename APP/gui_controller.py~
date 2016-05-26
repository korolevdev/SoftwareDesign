import sys
import time
import datetime
from fnmatch import fnmatch
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDateTime
from PyQt5 import uic
from gui import GUIController
from events import EvRender, EvSaveTLE, EvLoadTLE, EvReloadAll
from gui_qt_utils import QtScene, QtPalette
from queue import Queue


class QtGUIController(GUIController):

    def __init__(self):
        self.events = Queue()
        self.app = QApplication(sys.argv)

        self.w = uic.loadUi("main.ui")
        self.w.setAttribute(Qt.WA_DeleteOnClose, True)
        self.w.show()

        self.sattable = self.w.satTable
        self.satview = self.w.mapCanvas

        self.scene = QtScene(self.satview)
        self.pal = QtPalette()

        self.rendersats = set()
        self.satcolors = dict()

        hdr = self.sattable.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Fixed)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed)

        self.w.dtFrom.setDateTime(QDateTime.currentDateTimeUtc())
        self.w.dtTo.setDateTime(
            QDateTime.currentDateTimeUtc().addSecs(3600 * 2)
        )

        self.filters = ["*", "*", "*", "*"]

        self.selectall = False
        self.nosats = True
        self.colchange = False

        self.connect_sigs()

    def __del__(self):
        self.app.exit(0)

    def update(self):
        self.app.processEvents()

    def set_filter(self, fil):
        fil = [x.strip().upper() for x in fil]
        self.filters = list(map(lambda f: "*" if f in ["", None] else f, fil))
        for r in range(self.sattable.rowCount()):
            hide = False
            for c in range(1, len(self.filters)):
                str = self.sattable.item(r, c).text()
                if not fnmatch(str, self.filters[c]):
                    hide = True
                    break
            self.sattable.setRowHidden(r, hide)

    def clear_sats(self):
        self.rendersats.clear()
        self.satcolors.clear()
        self.sattable.setRowCount(0)
        self.scene.clear()
        self.nosats = True

    def set_sats(self, sats):
        for sat in sats:
            self.sat_insert(sat)
        self.nosats = False

    def show_error(self, s):
        msg = QMessageBox()
        msg.setWindowTitle("Error!")
        msg.setText(s)
        msg.setIcon(QMessageBox.Warning)
        msg.exec()

    # internal methods

    def sat_insert(self, sat):
        row = self.sattable.rowCount()
        self.sattable.insertRow(row)
        cb = QTableWidgetItem("")
        cb.setCheckState(Qt.Unchecked)
        self.sattable.setItem(row, 0, cb)
        self.sattable.setItem(
            row, 1,
            QTableWidgetItem(str(sat.norad))
        )
        self.sattable.setItem(
            row, 2,
            QTableWidgetItem(str(sat.intl))
        )
        self.sattable.setItem(
            row, 3,
            QTableWidgetItem(str(sat.name))
        )

    def render_sats(self, sats, time_a, time_b):
        self.scene.clear()
        for n, lines in sats:
            self.pal.set_fg_color(self.satcolors[n])
            self.scene.add_path(lines, self.pal.bg_pen, self.pal.fg_pen)

    # Qt slots

    def connect_sigs(self):
        hdr = self.sattable.horizontalHeader()
        hdr.sectionPressed.connect(self.slot_header_click)
        self.sattable.itemChanged.connect(self.slot_check_sat)
        self.w.destroyed.connect(self.slot_exit)
        self.w.fButton.pressed.connect(self.slot_set_filter)
        self.w.renderButton.pressed.connect(self.slot_render)
        self.w.saveButton.pressed.connect(self.slot_save)
        self.w.loadButton.pressed.connect(self.slot_load)
        self.w.refreshButton.pressed.connect(self.slot_refresh)

    def slot_render(self):
        time_a = self.w.dtFrom.dateTime().toMSecsSinceEpoch() / 1000
        time_b = self.w.dtTo.dateTime().toMSecsSinceEpoch() / 1000
        self.events.put(EvRender((time_a, time_b, self.rendersats)))

    def slot_set_filter(self):
        fil = ["*"]
        fil.append(self.w.fNoradEdit.text())
        fil.append(self.w.fIntlEdit.text())
        fil.append(self.w.fNameEdit.text())
        self.set_filter(fil)

    def slot_check_sat(self, item):
        if self.nosats:
            return
        if self.colchange:
            self.colchange = False
            return
        if item.column() != 0:
            return
        self.colchange = True
        row = item.row()
        chk = self.sattable.item(row, 0).checkState()
        norad = int(self.sattable.item(row, 1).text())
        if chk == Qt.Checked:
            self.rendersats.add(norad)
            self.satcolors[norad] = self.pal.wind()
            color = self.pal.color(self.satcolors[norad])
            item.setBackground(color)
        else:
            self.rendersats.discard(norad)
            self.satcolors.pop(norad)
            item.setBackground(Qt.transparent)
        self.w.saveButton.setEnabled(bool(self.rendersats))

    def slot_header_click(self, idx):
        if idx != 0:
            return
        self.selectall = not self.selectall
        chk = Qt.Checked if self.selectall else Qt.Unchecked
        for r in range(self.sattable.rowCount()):
            self.sattable.item(r, 0).setCheckState(chk)

    def slot_save(self):
        fname = QFileDialog.getSaveFileName(
            self.w,
            "Save TLE",
            ".",
            "TLE lists (*.txt *.tle *.tlelist)"
        )[0]
        if fname in ["", None]:
            return
        self.events.put(EvSaveTLE((self.rendersats, fname)))

    def slot_load(self):
        fname = QFileDialog.getOpenFileName(
            self.w,
            "Open TLE",
            "./selection.txt",
            "TLE lists (*.txt *.tle *.tlelist)"
        )[0]
        if fname in ["", None]:
            return
        self.events.put(EvLoadTLE(fname))

    def slot_refresh(self):
        self.events.put(EvReloadAll())

    def slot_exit(self):
        sys.exit(0)
