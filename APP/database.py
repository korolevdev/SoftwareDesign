import sqlite3 as sql
from datetime import datetime
from sgp import Sat, OrbitData

DBError = sql.Error


class DBController:

    def __init__(self, fname="sats.db"):
        self.dbfile = fname
        self.conn = sql.connect(
            fname, detect_types=sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        self.init_db()

    def __del__(self):
        self.conn.close()

    def init_db(self):
        self.c.execute(
            '''create table if not exists sats (
                   norad       integer not null primary key,
                   name        text,
                   intl        text,
                   country     text,
                   year        integer
               ) without rowid'''
        )
        self.c.execute(
            '''create table if not exists orbdata (
                   norad       integer not null,
                   date        integer,
                   epoch_yr    integer,
                   epoch_day   real,
                   bstar       real,
                   inclo       real,
                   nodeo       real,
                   ecco        real,
                   argpo       real,
                   ibexp       real,
                   mo          real,
                   no          real,
                   primary key (norad, date)
               ) without rowid'''
        )

    def get_all(self):
        sats = []
        self.c.execute("select * from sats")
        for rs in self.c.fetchall():
            sat = self.row_to_sat(rs)
            sats.append(sat)
        return sats

    def get_by_norad(self, norad):
        self.c.execute("select * from sats where norad = ?", (norad,))
        rs = self.c.fetchone()

    def get_orbits_between(self, norad, t_a, t_b):
        ld, rd = self.closest_orbit(norad, t_a), self.closest_orbit(norad, t_b)
        orbs = []
        res = self.c.execute(
            "select * from orbdata where norad = ? and date between ? and ? order by date",
            (norad, ld.timestamp, rd.timestamp)
        )
        return self.rows_to_orbdata(res)

    def get_orbit_latest(self, norad):
        self.c.execute(
            "select max(date), * from orbdata where norad = ?",
            (norad,)
        )
        rs = self.c.fetchone()
        orb = self.row_to_orbdata(rs[1:])
        return orb

    def get_orbits_all(self, norad):
        orbs = []
        res = self.c.execute("select * from orbdata where norad = ?", (norad,))
        return self.rows_to_orbdata(res)

    def get_orbits_closest(self, norad, time):
        orbs = []
        self.c.execute(
            '''select max(date), * from orbdata where norad = ?1 and date <= ?2
               union select min(date), * from orbdata where norad = ?1 and date >= ?2''',
            (norad, time)
        )
        res = self.c.fetchall()
        for rs in res:
            if rs[0] is None:
                continue
            orb = self.row_to_orbdata(rs[1:])
            orbs.append(orb)
        return orbs

    def sat_exists(self, norad):
        self.c.execute("select norad from sats where norad = ?", (norad,))
        return self.c.fetchone() is not None

    def sat_add(self, sat):
        self.c.execute(
            "insert or ignore into sats values (?, ?, ?, ?, ?)",
            (sat.norad, sat.name.rstrip(), sat.intl.rstrip(),
             sat.country.rstrip(), sat.year)
        )

    def orbdata_add(self, norad, orb):
        self.c.execute(
            "select max(date) from orbdata where norad = ?", (norad,))
        (latestdate,) = self.c.fetchone()
        if (latestdate is not None) and (latestdate > orb.timestamp):
            return
        self.c.execute(
            "insert or ignore into orbdata values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (norad, orb.timestamp, orb.epoch_yr, orb.epoch_day, orb.bstar,
             orb.inclo, orb.nodeo, orb.ecco, orb.argpo, 
             orb.ibexp, orb.mo, orb.no)
        )

    def add(self, sat):
        if not self.sat_exists(sat.norad):
            self.sat_add(sat)
        self.orbdata_add(sat.norad, sat.orbdata)

    def sync(self):
        self.conn.commit()

    # utils

    def closest_orbit(self, norad, t):
        if t is None:
            return self.get_orbit_latest(norad)
        corbs = self.get_orbits_closest(norad, t)
        if len(corbs) == 1:
            return corbs[0]
        ldt = abs(t - corbs[0].timestamp)
        rdt = abs(t - corbs[1].timestamp)
        return corbs[0] if ldt < rdt else corbs[1]

    def rows_to_orbdata(self, res):
        orbs = []
        for rs in res:
            orb = self.row_to_orbdata(rs)
            orbs.append(orb)
        return orbs

    def row_to_orbdata(self, rs):
        orb = OrbitData()
        (orb.norad, orb.timestamp, orb.epoch_yr, orb.epoch_day, orb.bstar,
         orb.inclo, orb.nodeo, orb.ecco, orb.argpo, orb.ibexp, 
         orb.mo, orb.no) = rs
        orb.init_date()
        return orb

    def row_to_sat(self, rs):
        sat = Sat(self.get_orbit_latest(rs[0]))
        (sat.norad, sat.name, sat.intl, sat.country, sat.year) = rs
        return sat