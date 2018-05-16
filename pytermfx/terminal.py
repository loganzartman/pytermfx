from pytermfx.color import Color, ColorMode
from pytermfx.adaptors import BaseAdaptor, PlatformAdaptor, STDIN, STDOUT
import sys

class Terminal:
    def __init__(self, input_file = STDIN, output_file = STDOUT):
        args = {
            "input_file": input_file,
            "output_file": output_file, 
            "resize_handler": self._handle_resize}
        self._resize_handlers = []

        try:
            self.adaptor = PlatformAdaptor(**args)
        except:
            self.adaptor = BaseAdaptor(**args)
        
        self.w = 0
        self.h = 0
        self._handle_resize()

    def add_resize_handler(self, func):
        """Adds a handler for terminal resize.
        """
        self._resize_handlers.append(func)
    
    def _handle_resize(self):
        if not self.update_size():
            return
        for h in self._resize_handlers:
            h()
    
    def managed(self):
        class TermManager:
            def __init__(self, term):
                self.term = term
            def __enter__(self):
                pass
            def __exit__(self, exc_type, exc_value, traceback):
                self.term.reset()
                if exc_type == KeyboardInterrupt:
                    return True
                return False
        return TermManager(self)
    
    def update_size(self, defaults=None):
        """Retrieve and store the dimensions of the terminal window.
        Sets self.w and self.h with current data if possible.
        Raises an exception if no size detection method works.
        """
        current_size = (self.w, self.h)

        # get new size
        try:
            size = self.adaptor.get_size()
        except:
            if defaults is not None:
                size = defaults
            else:
                raise
        
        # return whether size actually changed
        if size != current_size:
            self.w = size[0]
            self.h = size[1]
            return True
        return False

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
        self.adaptor.write(*things)
        return self

    def writeln(self, *things):
        """Writes an arbitrary number of things to the buffer with a newline.
        """
        self.adaptor.writeln(*things)
        return self

    def flush(self):
        """Flush the buffer to the terminal.
        """
        self.adaptor.flush()

    def print(self, *things, sep="", end="\n"):
        """Acts like Python's print(). Forces a flush.
        """
        self.adaptor.write(sep.join(str(t) for t in things), end)
        self.adaptor.flush()
        return self

    def clear(self):
        """Clear the screen.
        """
        self.adaptor.clear()
        return self 

    def clear_line(self):
        self.adaptor.clear_line()
        return self

    def clear_to_end(self):
        self.adaptor.clear_to_end()
        return self

    def reset(self):
        self.adaptor.reset()

    def cursor_set_visible(self, visible=True):
        self.adaptor.cursor_set_visible(visible)
        return self

    def cursor_get_pos(self):
        return self.adaptor.cursor_get_pos()

    def cursor_save(self):
        self.adaptor.cursor_save()
        return self

    def cursor_restore(self):
        self.adaptor.cursor_restore()
        return self

    def cursor_to(self, x, y):
        self.adaptor.cursor_to(x, y)
        return self

    def cursor_to_x(self, x):
        self.adaptor.cursor_to_x(x)
        return self

    def cursor_move(self, x, y):
        self.adaptor.cursor_move(x, y)
        return self

    def cursor_to_start(self):
        self.adaptor.cursor_to_start()
        return self
    
    def fill_box(self, x, y, w, h, ch):
        """Fills a region of the terminal
        """
        for i in range(max(int(y), 0), min(self.w, int(y+h))):
            self.adaptor.cursor_to(max(int(x), 0), i)
            self.adaptor.write(ch * min(min(w, w+x), self.w - x))
        return self

    def clear_box(self, x, y, w, h):
        self.fill_box(x, y, w, h, " ")
        return self
    
    def set_color_mode(self, mode):
        self.adaptor.set_color_mode(mode)

    def style(self, *styles):
        """Apply styles, which may be a Color or something with .ansi()
        Accepts a Color or a Style.
        """
        self.adaptor.style(*styles)
        return self

    def style_reset(self):
        """Reset style.
        """
        self.adaptor.style_reset()
        return self