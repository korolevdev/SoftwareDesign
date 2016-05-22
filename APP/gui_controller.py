from queue import Queue


class GUIController:

    def __init__(self):
        self.events = Queue()

    def __del__(self):
        pass

    def update(self):
        pass

    def poll_events(self):
        while not self.events.empty():
            yield self.events.get()

    def set_sats(self, sats):
        pass

    def set_filter(self, fil):
        pass

    def show_error(self, s):
        pass
