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
    
        self.collector = None
        self.grouper = None

    def _start(self):
        assert(not self.running)
        self.running = True

        if self.collector is not None:
            # the threads have shut down; wait for termination
            self.collector.join()
            self.grouper.join()

        # prepare and start new threads
        self.collector = Thread(target=self.collect_main, daemon=True)
        self.grouper = Thread(target=self.group_main, daemon=True)
        self.collector.start()
        self.grouper.start()
    
    def read(self, blocking=True):
        """Read a chunk of input from stdin.
        If blocking is set to false and no input is buffered, this will raise
        queue.Empty.

        InputDaemon groups temporally-close reads from stdin, so that key escape
        sequences sent by the terminal can be read in their entirety. This is
        crucial to parsing them, as they do not have unique prefixes. This is
        also similar to how libraries such as ncurses implement escape parsing.
        """
        # start up daemons lazily
        # this ensures that cbreak is set, etc. etc.
        if not self.running:
            self._start()
        
        if blocking:
            # block until some input is buffered
            while len(self.group_queue) == 0:
                self.input_event.wait()
        elif len(self.group_queue) == 0:
            # ensure that some input is buffered
            raise queue.Empty("No input buffered")

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
            try:
                ch = self.read_ch()        # blocks if stdin empty
            except:
                # exception indicates that terminal is not in cbreak!
                # therefore, shutdown threads and restart later.
                self.running = False       # mark as needing to restart threads
                self.input_queue.put(None) # sentinel to terminate grouper
                break                      # terminate collector
            
            self.input_queue.put(ch)       # blocks if queue full

    def group_main(self):
        # Grouper thread body
        buffer = []
        grouping = True
        timeout = None

        def dump_group():
            """Complete the current group of characters and dump to output.
            """
            nonlocal timeout, grouping
            if len(buffer) > 0:
                timeout = None
                grouping = False
                group = "".join(buffer)
                buffer.clear()
                self.group_queue.append(group)
                self.input_event.set()         # notify read() waiters

        while self.running:
            try:
                # wait up to timeout seconds for next char in group
                ch = self.input_queue.get(timeout = timeout)
                if ch is None:
                    # None indicates an error in collector; shutdown grouper
                    break
                if ch == chr(27):
                    # we have read an ESC; start a new group
                    # we can also immediately dump any previous group
                    dump_group()
                    timeout = self.buffer_timeout * 10 
                    grouping = True
                if len(buffer) == 2 and ch != "M":
                    # lower timeout if we are not reading a mouse input.
                    # this is essentially a heuristic but seems to work well.
                    timeout = self.buffer_timeout
                buffer.append(ch) # append character to group
                if not grouping:
                    dump_group()
            except queue.Empty:
                # timeout occurred; dump the group
                dump_group()

class InputAdaptor:
    def __init__(self, *args, read_func, **kwargs):
        super().__init__(*args, **kwargs)
        self._input = InputDaemon(read_func)
    
    def getch_raw(self):
        return self._input.read()