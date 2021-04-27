
class NoCache:
    """ Dummy cache for CachedSession, doing nothing. """
    def __init__(self):
        pass

    def get(self, key):
        return None

    def set(self, key, value):
        pass

