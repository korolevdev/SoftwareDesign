from sgp import Sat


class Decoder:

    def __init__(self, decoders=[]):
        self.decoders = decoders

    def decode(self, fmt, str):
        dec = self.pick_decoder(fmt)
        if dec is None:
            raise NoDecoderError(fmt)
        return dec.decode(str)


class DecoderGeneric:
    fmt = "text"

    def decode(self, str):
        return [Sat()]
