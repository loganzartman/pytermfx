from pytermfx.color import Color, ColorMode
from pytermfx.adaptors import BaseAdaptor, PlatformAdaptor, STDIN, STDOUT
import sys

class Terminal:
    def __init__(self, input_file = STDIN, output_file = STDOUT):
        args = {
            "input_file": input_file,
            "output_file": output_file, 
            "resize_handler": self.update_size}
        
        try:
            self.adaptor = PlatformAdaptor(**args)
        except:
            self.adaptor = BaseAdaptor(**args)

        self._resize_handlers = [self.update_size]
        self.update_size()

    def add_resize_handler(self, func):
        """Adds a handler for terminal resize.
        """
        self._resize_handlers.append(func)
    
    def _handle_resize(self):
        for h in self._resize_handlers:
            h()
    
    def update_size(self, defaults=None):
        """Retrieve and store the dimensions of the terminal window.
        Sets self.w and self.h with current data if possible.
        Raises an exception if no size detection method works.
        """
        try:
            self.w, self.h = self.adaptor.get_size()
        except:
            if defaults is not None:
                self.w, self.h = defaults
            else:
                raise
    
    def set_cbreak(self, cbreak=True):
        return self.adaptor.set_cbreak(cbreak)

    def mouse_enable(self, mode="move"):
        return self.adaptor.mouse_enable(mode)

    def getch(self):
        """Get a single character from stdin in cbreak mode.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        return self.adaptor.getch()

    def getch_raw(self):
        """Get a single character from stdin in cbreak mode.
        Does not decode escape sequences.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        return self.adaptor.getch_raw()
    
    def write(self, *things):
        """Write an arbitrary number of things to the buffer.
        """
        return self.adaptor.write(*things)

    def writeln(self, *things):
        """Writes an arbitrary number of things to the buffer with a newline.
        """
        return self.adaptor.writeln(*things)

    def flush(self):
        """Flush the buffer to the terminal.
        """
        return self.adaptor.flush()

    def print(self, *things, sep="", end="\n"):
        """Acts like Python's print(). Forces a flush.
        """
        return self.adaptor.write(sep.join(things), end).flush()

    def clear(self):
        """Clear the screen.
        """
        return self.adaptor.clear() 

    def clear_line(self):
        return self.adaptor.clear_line()

    def clear_to_end(self):
        return self.adaptor.clear_to_end()

    def reset(self):
        return self.adaptor.reset()

    def cursor_set_visible(self, visible=True):
        return self.adaptor.cursor_set_visible(visible)

    def cursor_get_pos(self):
        return self.adaptor.cursor_get_pos()

    def cursor_save(self):
        return self.adaptor.cursor_save()

    def cursor_restore(self):
        return self.adaptor.cursor_restore()

    def cursor_to(self, x, y):
        return self.adaptor.cursor_to(x, y)

    def cursor_to_x(self, x):
        return self.adaptor.cursor_to_x(x)

    def cursor_move(self, x, y):
        return self.adaptor.cursor_move(x, y)

    def cursor_to_start(self):
        return self.cursor_to_start()
    
    def fill_box(self, x, y, w, h, ch):
        """Fills a region of the terminal
        """
        for i in range(max(int(y), 0), min(self.w, int(y+h))):
            self.adaptor.cursor_to(max(int(x), 0), i)
            self.adaptor.write(ch * min(min(w, w+x), self.w - x))
        return self

    def clear_box(self, x, y, w, h):
        return self.fill_box(x, y, w, h, " ")

    def style(self, *styles):
        """Apply styles, which may be a Color or something with .ansi()
        Accepts a Color or a Style.
        """
        return self.adaptor.style(*styles)

    def style_reset(self):
        """Reset style.
        """
        return self.adaptor.style()