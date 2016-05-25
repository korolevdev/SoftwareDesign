from sgp import Sat


class DecoderError(Exception):

    def __init__(self, err):
        self.value = err

    def __str__(self):
        return repr(self.value)


class NoDecoderError(DecoderError):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "no suitable decoder for " + repr(self.value)


class EncodedValueError(DecoderError):

    def __init__(self, fmt, err, pos=None):
        self.value = fmt
        self.err = err
        self.pos = pos

    def __str__(self):
        if self.pos is not None:
            return repr(self.value) + ": " + self.err + " at " + str(self.pos)
        else:
            return repr(self.value) + ": " + self.err

class Decoder:

    def __init__(self, decoders=[]):
        self.decoders = decoders

    def pick_decoder(self, fmt):
        return next((x for x in self.decoders if x.fmt == fmt), None)

    def decode(self, fmt, str):
        dec = self.pick_decoder(fmt)
        if dec is None:
            raise NoDecoderError(fmt)
        return dec.decode(str)


class DecoderGeneric:
    fmt = "text"

    def decode(self, str):
        return [Sat()]
