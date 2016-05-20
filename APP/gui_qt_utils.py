from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsPathItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QPen, QColor


class QtPalette:

    def __init__(self, ncolors=12, bw=9, fw=3):
        self.pal = []
        self.pal_idx = 0
        self.fg_pen = QPen(QColor(220, 220, 220))
        self.bg_pen = QPen(QColor(0, 0, 0))
        self.bg_pen.setWidth(bw)
        self.fg_pen.setWidth(fw)
        self.generate(ncolors)

    def generate(self, nc):
        for i in range(0, 256, 256 // nc):
            col = QColor()
            col.setHsv(i % 256, 255, 255)
            self.pal.append(col)

    def wind(self):
        c = self.pal_idx
        self.pal_idx = (self.pal_idx + 1) % len(self.pal)
        return c

    def unwind(self):
        c = self.pal_idx
        self.pal_idx = c - 1 if c > 0 else len(self.pal) - 1
        return c

    def color(self, idx):
        idx %= len(self.pal)
        return self.pal[idx]

    def set_bg_color(self, idx):
        self.bg_pen.setColor(self.color(idx))

    def set_fg_color(self, idx):
        self.fg_pen.setColor(self.color(idx))


class QtScene:

    def __init__(self, view):
        self.scene = QGraphicsScene()
        self.view = view
        self.map = None
        self.curves = []
        self.view.setScene(self.scene)
        self.load_res()

    def load_res(self, mapf="map.png"):
        img = QImage(mapf)
        pix = QPixmap.fromImage(img)
        self.map = QGraphicsPixmapItem(pix)
        self.scene.addItem(self.map)
        self.view.fitInView(self.map)
        self.view.centerOn(self.map)

    def add_path(self, lines, bg_pen, fg_pen):
        qpath = self.linelist_to_qpath(lines)
        bpi = QGraphicsPathItem(qpath)
        bpi.setPen(bg_pen)
        fpi = QGraphicsPathItem(qpath)
        fpi.setPen(fg_pen)
        self.curves += [bpi, fpi]
        self.scene.addItem(bpi)
        self.scene.addItem(fpi)
        self.view.fitInView(self.map)
        self.view.centerOn(self.map)

    def clear(self):
        for c in self.curves:
            self.scene.removeItem(c)
        self.curves = []

    def linelist_to_qpath(self, llst):
        w = self.map.boundingRect().width()
        h = self.map.boundingRect().height()
        w2 = w / 2
        h2 = h / 2
        path = QPainterPath()
        if not llst:
            return path
        for ln in llst:
            path.moveTo(ln.x1 * w2 + w2, h2 - ln.y1 * h2)
            path.lineTo(ln.x2 * w2 + w2, h2 - ln.y2 * h2)
        return path
