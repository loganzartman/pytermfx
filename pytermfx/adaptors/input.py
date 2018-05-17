from pytermfx.adaptors.base import BaseAdaptor
from functools import partial
from threading import Thread, Event
from multiprocessing import Queue
from time import process_time
import queue

class InputDaemon:
    def __init__(self, read_ch_func):
        self.read_ch = read_ch_func

        self.input_event = Event()              # used to block until input
        self.input_queue = Queue(maxsize = 256) # input read by collector
        self.buffer_timeout = 0.005             # group timeout in seconds
        self.group_queue = []                   # groups of input from grouper
        self.running = False
    
        # Prepare threads
        self.grouper = Thread(target=self.group_main, daemon=True)
        self.collector = Thread(target=self.collect_main, daemon=True)

    def _start(self):
        self.running = True
        self.grouper.start()
        self.collector.start()
    
    def read(self):
        # start up daemons lazily
        # this ensures that cbreak is set, etc. etc.
        if not self.running:
            self._start()
        
        self.input_event.wait() # block until some input is buffered
        if len(self.group_queue) == 0:
            # sometimes we are notified erroneously
            return ""

        # poll input queue
        group = self.group_queue.pop(0)
        if len(self.group_queue) == 0:
            # no more input for now
            self.input_event.clear()
        return group
    
    def collect_main(self):
        # Collector thread body
        while self.running:
            # read character from stdin and enqueue
            ch = self.read_ch()      # blocks if stdin empty
            self.input_queue.put(ch) # blocks if queue full

    def group_main(self):
        # Grouper thread body
        buffer = []
        grouping = True
        timeout = 0

        def dump_group():
            """Complete the current group of characters and dump to output.
            """
            nonlocal timeout
            if len(buffer) > 0:
                timeout = 0
                group = "".join(buffer)
                buffer.clear()
                self.group_queue.append(group)
                self.input_event.set()         # notify read() waiters

        while self.running:
            try:
                # wait up to timeout seconds for next char in group
                ch = self.input_queue.get(timeout = timeout)
                if ch == chr(27):
                    # we have read an ESC; start a new group
                    # we can also immediately dump any previous group
                    dump_group()
                    timeout = self.buffer_timeout * 10
                    grouping = True
                if len(buffer) == 2 and ch != "M":
                    timeout = self.buffer_timeout
                buffer.append(ch) # append character to group
            except queue.Empty:
                # timeout occurred; dump the group
                dump_group()
                grouping = False

class InputAdaptor:
    def __init__(self, *args, read_func, **kwargs):
        super().__init__(*args, **kwargs)
        self._input = InputDaemon(read_func)
    
    def getch_raw(self):
        return self._input.read()