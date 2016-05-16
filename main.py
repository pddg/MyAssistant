from queue import Queue
from threading import Thread
import time
from lib.stream import tweetassembler, StreamRecieverThread


class CoreThread(Thread):

    def __init__(self, queue):
        super(CoreThread, self).__init__()
        self.daemon = True
        self.queue = queue

    def run(self):
        while True:
            obj = self.queue.get()
            tweetassembler(obj)


def StartThreads():
    q = Queue()
    CoreTh = CoreThread(q)
    StreamTh = StreamRecieverThread(q)
    CoreTh.start()
    StreamTh.start()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    StartThreads()
