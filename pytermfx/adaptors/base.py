from functools import partial
from pytermfx.escapes import parse_escape
import os

class BaseAdaptor:
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        self.in_file = input_file
        self.out_file = output_file
        self.resize_handler = resize_handler
        self._buffer = []
        self._cbreak = False
        self._getch_buffer = []

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
        return NotImplemented

    def getch(self):
        """Get a single character from stdin in cbreak mode.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        # read and buffer control sequences
        while len(self._getch_buffer) == 0:
            self._getch_buffer += parse_escape(self.getch_raw())
        return self._getch_buffer.pop(0)

    def getch_raw(self):
        """Get a single character sequence from stdin in cbreak mode.
        Does not decode escape sequences.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        return NotImplemented
    
    def readch(self):
        """Get a single character from stdin in cbreak mode.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        return NotImplemented

    def write(self, *things):
        """Write an arbitrary number of things to the buffer.
        """
        self._buffer += map(lambda i: str(i), things)

    def writeln(self, *things):
        """Writes an arbitrary number of things to the buffer with a newline.
        """
        self.write(*things, os.linesep)

    def flush(self):
        """Flush the buffer to the terminal.
        """
        print("".join(self._buffer), end="", file=self.out_file, flush=True)
        self._buffer = []

    def clear(self):
        """Clear the screen.
        """
        return NotImplemented

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
        return NotImplemented

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
    
    def set_color_mode(self, mode):
        """Change the color mode of the terminal.
        The color mode determines what kind of ANSI sequences are used to
        set colors. See ColorMode for more details.
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