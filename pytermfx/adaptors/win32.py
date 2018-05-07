from pytermfx.adaptors.base import BaseAdaptor
from ctypes import windll, Structure, c_short, c_ushort, byref

k32 = windll.kernel32

# structs from wincon.h
class COORD(Structure):
    _fields_ = [
        ("X", c_short),
        ("Y", c_short)
    ]

class SMALL_RECT(Structure):
    _fields_ = [
        ("Left", c_ushort),
        ("Top", c_ushort),
        ("Right", c_ushort),
        ("Bottom", c_ushort)
    ]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", c_ushort),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)
    ]

class Win32Adaptor(BaseAdaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)
        self.in_file = input_file
        self.out_file = output_file
        self.resize_handler = resize_handler
        self._buffer = []

    def mouse_enable(self, mode):
        """Enable experimental mouse support.
        """
        return NotImplemented

    def mouse_disable(self):
        """Disable experimental mouse support.
        """
        return NotImplemented
    
    def set_cbreak(self, cbreak):
        """Enable or disable cbreak mode.
        """
        return NotImplemented

    def get_size(self, defaults=None):
        """Retrieve the dimensions of the terminal window.
        Raises an exception if no size detection method works.
        """
        info = CONSOLE_SCREEN_BUFFER_INFO()
        k32.GetConsoleScreenBufferInfo(self.out_file, byref(info))
        w = info.srWindow.Right - info.srWindow.Left
        h = info.srWindow.Bottom - info.srWindow.Top
        return (w, h)

    def getch(self):
        """Get a single character from stdin in cbreak mode.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        return NotImplemented

    def getch_raw(self):
        """Get a single character from stdin in cbreak mode.
        Does not decode escape sequences.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        return NotImplemented

    def flush(self):
        """Flush the buffer to the terminal.
        """
        msg = "".join(self._buffer)
        written = c_short()
        k32.WriteConsoleW(
            self.out_file,
            msg,
            c_short(len(msg)),
            byref(written),
            None
        )
        self._buffer = []

    def clear(self):
        """Clear the screen.
        """
        pass # TODO: replace no-op

    def clear_line(self):
        """Clear the line and move cursor to start
        """
        return NotImplemented

    def clear_to_end(self):
        """Clear to the end of the line
        """
        return NotImplemented

    def reset(self):
        """Clean up the terminal state before exiting.
        """
        pass

    def cursor_set_visible(self, visible=True):
        """Change the cursor visibility.
        visible may be True or False.
        """
        return NotImplemented

    def cursor_get_pos(self):
        """Retrieve the current (x,y) cursor position.
        This is slow, so avoid using when unnecessary.
        """
        return NotImplemented

    def cursor_save(self):
        """Save the cursor position
        """
        return NotImplemented

    def cursor_restore(self):
        """Restore the cursor position
        """
        return NotImplemented

    def cursor_to(self, x, y):
        """Move the cursor to an absolute position.
        """
        self.flush()
        pos = COORD(X=x, Y=y)
        k32.SetConsoleCursorPosition(self.out_file, pos)
        return self

    def cursor_to_x(self, x):
        """Move the cursor to a given column on the same line.
        """
        return NotImplemented

    def cursor_move(self, x, y):
        """Move the cursor by a given amount.
        """
        return NotImplemented

    def cursor_to_start(self):
        """Move the cursor to the start of the line.
        """
        return NotImplemented

    def style(self, *styles):
        """Apply styles, which may be a Color or something with .ansi()
        Accepts a Color or a Style.
        """
        return NotImplemented

    def style_reset(self):
        """Reset style.
        """
        return NotImplemented