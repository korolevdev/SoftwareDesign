from math import fmod, pi


class AppException(Exception):
    pass


def jt_to_gmst(jt):
    dpi = 2 * pi
    tut1 = (jt - 2451545.0) / 36525.0
    temp = -6.2e-6 * tut1 * tut1 * tut1 + 0.093104 * \
        tut1 * tut1 + 3164400184.812866 * tut1 + 67310.54841
    temp = fmod(temp * pi / 43200.0, dpi)

    if temp < 0.0:
        temp += dpi

    return temp - pi / 4

def tle_checksum(ln):
    s = 0
    for c in ln:
        if c.isdigit():
            s += int(c)
        elif c == '-':
            s += 1
    return s % 10