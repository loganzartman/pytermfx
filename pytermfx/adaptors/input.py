from pytermfx.adaptors.base import BaseAdaptor
from functools import partial
from threading import Thread, Event
from multiprocessing import Queue
from time import process_time
import queue

class InputDaemon:
    def __init__(self, read_ch_func):
        self.read_ch = read_ch_func
        self.grouper = Thread(target = self.group_main, daemon = True)
        self.collector = Thread(target = self.collect_main, daemon = True)

        self.input_event = Event()               # used to block until input
        self.input_queue = Queue(maxsize = 256)  # input read by collector
        self.buffer_timeout = 0.001              # group timeout in seconds
        self.group_queue = []                    # groups of input from grouper
        self.running = False

    def _start(self):
        self.running = True
        self.grouper.start()
        self.collector.start()        
    
    def read(self):
        # start up daemons lazily
        if not self.running:
            self._start()
        
        self.input_event.wait() # block until some input is buffered
        if len(self.group_queue) == 0:
            return ""

        # poll input queue
        group = self.group_queue.pop(0)
        if len(self.group_queue) == 0:
            self.input_event.clear()
        return group
    
    def collect_main(self):
        while self.running:
            # read character
            ch = self.read_ch()
            self.input_queue.put(ch)
    
    def group_main(self):
        buffer = []
        while self.running:
            try:
                ch = self.input_queue.get(timeout = self.buffer_timeout)
                buffer.append(ch)
            except queue.Empty:
                if len(buffer) > 0:
                    group = "".join(buffer)
                    buffer.clear()
                    self.group_queue.append(group)
                    self.input_event.set()

class InputAdaptor:
    def __init__(self, *args, read_func, **kwargs):
        super().__init__(*args, **kwargs)
        self._input = InputDaemon(read_func)
    
    def getch_raw(self):
        return self._input.read()