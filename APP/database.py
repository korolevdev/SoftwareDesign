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