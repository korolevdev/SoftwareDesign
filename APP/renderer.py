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

class Renderer:

    def __init__(self, steps=150, mres=4):
        self.min_resolutions = mres
        self.steps = steps
        self.step = 0
        self.jstep = 0
        self.line_list = []