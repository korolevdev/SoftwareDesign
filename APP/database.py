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