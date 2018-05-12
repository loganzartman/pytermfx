from pytermfx.constants import *
from pytermfx.adaptors.vt100 import VT100Adaptor
from threading import RLock
import signal
import termios
import tty

size_lock = RLock()

class UnixAdaptor(VT100Adaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)

        self._original_attr = termios.tcgetattr(self.in_file)
        signal.signal(signal.SIGWINCH, lambda s,f: self.resize_handler())
    
    def set_cbreak(self, cbreak):
        """Enable or disable cbreak mode.
        """
        assert(self._original_attr != None)
        termios.tcsetattr(self.in_file, termios.TCSADRAIN, self._original_attr)
        if cbreak:
            tty.setcbreak(self.in_file.fileno())
        self._cbreak = cbreak
    
    def getch_raw(self):
        """Get a single character from stdin in cbreak mode.
        Does not decode escape sequences.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        if not self._cbreak:
            raise ValueError("Must be in cbreak mode.")
        return self.in_file.read(1)
    
    def get_size(self, defaults=None):
        """Retrieve the dimensions of the terminal window.
        Raises an exception if no size detection method works.
        """
        global size_lock
        size_lock.acquire()
        try:
            self.cursor_save()
            self.cursor_to(9999, 9999)
            x, y = self.cursor_get_pos()
            w = x + 1
            h = y + 1
            self.cursor_restore()
            return (w, h)
        except:
            raise RuntimeError("Failed to get terminal size.")
        finally:
            size_lock.release()
    
    def cursor_get_pos(self):
        old_status = self._cbreak
        if not self._cbreak:
            self.set_cbreak(True)
        termios.tcflush(self.in_file, termios.TCIOFLUSH)
        
        # write DSR (device status report)
        self.write(CSI, "6n")
        self.flush()

        # read result from stdin
        buf = []
        while self.getch_raw() != "[": # skip start
            pass
        c = ""
        while c != "R": # read until end
            buf.append(c)
            c = self.getch_raw()
        parts = "".join(buf).split(";")

        # restore old cbreak
        if not old_status:
            self.set_cbreak(False)

        return (int(parts[1]) - 1, int(parts[0]) - 1)