#!/usr/bin/env python3

import sys
from satellite import Sat
from dbcontroller import DBController, DBError
from decoder import Decoder, DecoderError
from tledecoder import TLEDecoder, TLEListDecoder
from downloader import Downloader, EncodedSatData, DownloaderError


def main():
    dbc = DBController()
    dec = Decoder([TLEDecoder(), TLEListDecoder()])

    dlc = None

    try:
        dlc = Downloader()
    except DownloaderError as e:
        print("failed to initialize downloader: " + str(e))
        sys.exit(1)

    for esat in dlc.get_data():
        sats = []
        try:
            sats = dec.decode(esat.fmt, esat.data)
        except DecoderError as e:
            print("failed to decode: " + str(e))

        try:
            for sat in sats:
                dbc.add(sat)
            dbc.sync()
        except DBError as e:
            print("failed to insert into db: " + str(e))

if __name__ == "__main__":
    main()
