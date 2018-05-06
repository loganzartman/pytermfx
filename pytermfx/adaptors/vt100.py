from pytermfx.adaptors.base import BaseAdaptor
from pytermfx.constants import *
from pytermfx.color import ColorMode, Color
from pytermfx.escapes import read_escape
import signal
import termios
import tty

class VT100Adaptor(BaseAdaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)
        self._cbreak = False
        self._color_mode = ColorMode.MODE_256
        self._cursor_visible = False
        self._mouse = None
        self._buffer = []
        self._original_attr = termios.tcgetattr(self.in_file)
        
        signal.signal(signal.SIGWINCH, lambda s,f: self.resize_handler())
    
    def mouse_enable(self, mode = "move"):
        """Enable experimental mouse support.
        """
        if not self._cbreak:
            raise ValueError("Must be in cbreak mode.")
        MODE_MAP = {
            "click": "?1001h",
            "drag":  "?1002h",
            "move":  "?1003h"}
        assert(mode in MODE_MAP)
        self._mouse = mode
        self.write(CSI, MODE_MAP[mode]) # read movements
        self.write(CSI, "?1005h") # use UTF-8 encoding
        self.flush()

    def mouse_disable(self):
        """Disable experimental mouse support.
        """
        if not self._mouse:
            return
        # disable mouse
        self.write(CSI, "?1001l") 
        self.write(CSI, "?1002l") 
        self.write(CSI, "?1003l") 
        self.flush()
        self._mouse = None
    
    def set_cbreak(self, cbreak):
        """Enable or disable cbreak mode.
        """
        assert(self._original_attr != None)
        termios.tcsetattr(self.in_file, termios.TCSADRAIN, self._original_attr)
        if cbreak:
            tty.setcbreak(self.in_file.fileno())
        self._cbreak = cbreak
    
    def set_color_mode(self, mode):
        """Change the color mode of the terminal.
        The color mode determines what kind of ANSI sequences are used to
        set colors. See ColorMode for more details.
        """
        if not isinstance(mode, ColorMode):
            raise ValueError("mode must be a ColorMode.")
        self._color_mode = mode
    
    def get_size(self, defaults=None):
        """Retrieve the dimensions of the terminal window.
        Raises an exception if no size detection method works.
        """
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

    def getch(self):
        """Get a single character from stdin in cbreak mode.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        if not self._cbreak:
            raise ValueError("Must be in cbreak mode.")
        return read_escape(self.in_file)

    def getch_raw(self):
        """Get a single character from stdin in cbreak mode.
        Does not decode escape sequences.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        if not self._cbreak:
            raise ValueError("Must be in cbreak mode.")
        return self.in_file.read(1)

    def clear(self):
        """Clear the screen.
        """
        self.write(CSI, "2J")
        return self

    def clear_line(self):
        self.cursor_to_start()
        self.write(CSI, "2K")
        return self

    def clear_to_end(self):
        self.write(CSI, "0K")
        return self

    def reset(self):
        self.cursor_to(0, 0)
        self.clear()
        self.set_cbreak(False)
        self.mouse_disable()
        self.write(ESC, "c") # reset state
        self.flush()

    def cursor_set_visible(self, visible=True):
        self.write(CSI, "?25", "h" if visible else "l")
        self._cursor_visible = visible
        return self

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

    def cursor_save(self):
        self.write(CSI, "s")
        return self

    def cursor_restore(self):
        self.write(CSI, "u")
        return self

    def cursor_to(self, x, y):
        self.write(CSI, int(y+1), ";", int(x+1), "H")
        return self

    def cursor_to_x(self, x):
        self.write(CSI, int(x+1), "G")
        return self

    def cursor_move(self, x, y):
        if x < 0:
            self.write(CSI, abs(int(x)), "D")
        elif x > 0:
            self.write(CSI, int(x), "C")
        if y < 0:
            self.write(CSI, abs(int(x)), "A")
        elif y > 0:
            self.write(CSI, int(x), "B")
        return self

    def cursor_to_start(self):
        self.write(CSI, "1G")
        return self

    def style(self, *styles):
        """Apply styles, which may be a Color or something with .ansi()
        Accepts a Color or a Style.
        """
        for style in styles:
            if isinstance(style, Color):
                self.write(style.to_mode(self._color_mode))
            else:
                self.write(style.ansi())
        return self

    def style_reset(self):
        """Reset style.
        """
        self.write(CSI, "0m")
        return self