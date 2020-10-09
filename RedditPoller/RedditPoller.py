import time

from RedditPoller.Retry import retry

POLL_LIMIT = 50

class FifoSet:
    def __init__(self, size):
        self.size = size
        self._fifo = []
        self._set = set()

    def __contains__(self, item):
        return item in self._set

    def add(self, item):
        if len(self._set) == self.size:
            self._set.remove(self._fifo.pop(0))
        self._fifo.append(item)
        self._set.add(item)


class RedditPoller:
    def __init__(self, function, before = None):
        self.function = function
        self.seenNames = FifoSet(POLL_LIMIT * 2)
        self.beforeName = before

    def getLatest(self):
        while True:
            newestName = None
            for item in self._poll():
                if item.name in self.seenNames:
                    continue
                self.seenNames.add(item.name)
                newestName = item.name
                yield item

            self.beforeName = newestName
            yield None

    @retry
    def _poll(self):
        return reversed(list(self.function(limit = POLL_LIMIT, params = { "before": self.beforeName })))