from math import fabs
from datetime import datetime, timezone
from sgp4.ext import jday
from coordinates import wgs84_to_ndc


class Line:

    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def clamp(self):
        if (self.y2 < self.y1):
            self.x1, self.x2 = self.x2, self.x1,
            self.y1, self.y2 = self.y2, self.y1

        if (self.y1 > 1) or (self.y2 < -1):
            return None

        if self.x1 == self.x2:
            return self

        if self.y2 > 1:
            self.x2, self.y2 = self.x1 + \
                (1 - self.y1) / (self.y2 - self.y1) * (self.x2 - self.x1), 1

        if self.y1 < -1:
            self.x1, self.y1 = self.x1 - \
                (1 + self.y1) / (self.y2 - self.y1) * (self.x2 - self.x1), -1

        return self

class Renderer:

    def __init__(self, steps=150, mres=4):
        self.min_resolutions = mres
        self.steps = steps
        self.step = 0
        self.jstep = 0
        self.line_list = []

    def get_coord(self, t, jt, odata):
        pos, _ = odata.propagate(datetime.fromtimestamp(t, timezone.utc))
        return wgs84_to_ndc(pos, jt)

    def get_lines(self, x1, y1, x2, y2):
        if (x1 > x2):
            x1, x2, y1, y2 = x2, x1, y2, y1

        ret = []
        l1, l2 = None, None
        if fabs(x1 + 2 - x2) < fabs(x1 - x2):
            if fabs(x2 - x1 - 2) > 0:
                yc = y1 - (1 + x1) / (x2 - x1 - 2) * (y2 - y1)
                l1 = Line(-1, yc, x1, y1).clamp()
                l2 = Line(x2, y2, 1, yc).clamp()
        else:
            l1 = Line(x1, y1, x2, y2).clamp()
        if l1 is not None:
            ret.append(l1)
        if l2 is not None:
            ret.append(l2)

        return ret