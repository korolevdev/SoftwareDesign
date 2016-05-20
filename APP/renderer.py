from math import fabs
from datetime import datetime, timezone
from sgp4.ext import jday
from coordconv import wgs84_to_ndc


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

    def render_border(self, t1, t2, jt1, jt2, odata):
        if (t1 >= t2):
            return

        tn, jtn = t1 + self.step, jt1 + self.jstep
        xp, yp = self.get_coord(t1, jt1, odata)

        while tn < t2:
            xn, yn = self.get_coord(tn, jtn, odata)
            self.line_list += self.get_lines(xp, yp, xn, yn)
            xp, yp = xn, yn
            tn, jtn, = tn + self.step, jtn + self.jstep

        xn, yn = self.get_coord(t2, jtn, odata)

        self.line_list += self.get_lines(xp, yp, xn, yn)

    def get_coords_from_nearest(self, t, jt, odata1, odata2):
        if t - odata1.timestamp < odata2.timestamp - t:
            return self.get_coord(t, jt, odata2)

        return self.get_coord(t, jt, odata1)

    def render_mid(self, t1, t2, jt1, jt2, odata1, odata2):
        if (t1 >= t2):
            return

        tn, jtn = t1 + self.step, jt1 + self.jstep
        xp, yp = self.get_coords_from_nearest(t1, jt1, odata1, odata2)

        while tn < t2:
            xn, yn = self.get_coords_from_nearest(tn, jtn, odata1, odata2)
            self.line_list += self.get_lines(xp, yp, xn, yn)
            xp, yp = xn, yn
            tn, jtn = tn + self.step, jtn + self.jstep

        xn, yn = self.get_coords_from_nearest(t2, jtn, odata1, odata2)

        self.line_list += self.get_lines(xp, yp, xn, yn)

    def set_steps(self, no):
        if no < self.min_resolutions:
            no = self.min_resolutions

        self.jstep = 1.0 / no / self.steps
        self.step = 86400.0 * self.jstep

    def render(self, t1, t2, odata_list):
        if (len(odata_list) == 0) or (t2 <= t1):
            return []

        next_odata = odata_list[0]
        next_time, next_jtime = next_odata.timestamp, next_odata.jdate

        dt1 = datetime.fromtimestamp(t1, timezone.utc)
        dt2 = datetime.fromtimestamp(t2, timezone.utc)
        jt1 = jday(dt1.year, dt1.month, dt1.day,
                   dt1.hour, dt1.minute, dt1.second)
        jt2 = jday(dt2.year, dt2.month, dt2.day,
                   dt2.hour, dt2.minute, dt2.second)

        self.set_steps(next_odata.no)
        self.line_list = []

        if (next_time < t1) or (next_time > t2):
            self.render_border(t1, t2, jt1, jt2, next_odata)
            return self.line_list

        self.render_border(t1, next_time, jt1, next_jtime, next_odata)

        i = 1
        imax = len(odata_list)
        while i < imax:
            prev_odata, prev_time, prev_jtime = next_odata, next_time, next_jtime
            next_odata = odata_list[i]
            next_time, next_jtime = next_odata.timestamp, next_odata.jdate

            self.render_mid(prev_time, next_time, prev_jtime,
                            next_jtime, prev_odata, next_odata)

            i += 1

        self.render_border(next_time, t2, next_jtime, jt2, next_odata)

        return self.line_list
