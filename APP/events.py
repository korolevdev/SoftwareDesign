class Event:

    def __init__(self, data=None):
        self.data = data

    def process(self, core):
        pass


class EvRender(Event):

    def process(self, core):
        time_a = self.data[0]
        time_b = self.data[1]
        sats = []
        for n in self.data[2]:
            orbs = core.dbc.get_orbits_between(n, time_a, time_b)
            lines = core.rdr.render(time_a, time_b, orbs)
            sats.append((n, lines))
        core.gui.render_sats(sats, time_a, time_b)


class EvReloadAll(Event):

    def process(self, core):
        core.reload_sats()


class EvSaveTLE(Event):

    def process(self, core):
        core.save_tle(self.data[0], self.data[1])


class EvLoadTLE(Event):

    def process(self, core):
        core.load_tle(self.data)
