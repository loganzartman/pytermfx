from pytermfx.adaptors.base import BaseAdaptor
from pytermfx.constants import *
from pytermfx.color import ColorMode, Color

class VT100Adaptor(BaseAdaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)
        self._color_mode = ColorMode.MODE_256
        self._cursor_visible = False
        self._mouse = None
    
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
    
    def set_color_mode(self, mode):
        """Change the color mode of the terminal.
        The color mode determines what kind of ANSI sequences are used to
        set colors. See ColorMode for more details.
        """
        if not isinstance(mode, ColorMode):
            raise ValueError("mode must be a ColorMode.")
        self._color_mode = mode

    def clear(self):
        """Clear the screen.
        """
        self.write(CSI, "2J")

    def clear_line(self):
        self.cursor_to_start()
        self.write(CSI, "2K")

    def clear_to_end(self):
        self.write(CSI, "0K")

    def reset(self):
        self.flush()
        self.set_cbreak(False)
        self.mouse_disable()
        self.style_reset()
        self.cursor_set_visible(True)
        self.flush()
        # self.write(ESC, "c") # reset state

    def cursor_set_visible(self, visible=True):
        self.write(CSI, "?25", "h" if visible else "l")
        self._cursor_visible = visible

    def cursor_save(self):
        self.write(CSI, "s")

    def cursor_restore(self):
        self.write(CSI, "u")

    def cursor_to(self, x, y):
        self.write(CSI, int(y+1), ";", int(x+1), "H")

    def cursor_to_x(self, x):
        self.write(CSI, int(x+1), "G")

    def cursor_move(self, x, y):
        if x < 0:
            self.write(CSI, abs(int(x)), "D")
        elif x > 0:
            self.write(CSI, int(x), "C")
        if y < 0:
            self.write(CSI, abs(int(x)), "A")
        elif y > 0:
            self.write(CSI, int(x), "B")

    def cursor_to_start(self):
        self.write(CSI, "1G")

    def style(self, *styles):
        """Apply styles, which may be a Color or something with .ansi()
        Accepts a Color or a Style.
        """
        for style in styles:
            if isinstance(style, Color):
                self.write(style.to_mode(self._color_mode))
            else:
                self.write(style.ansi())

    def style_reset(self):
        """Reset style.
        """
        self.write(CSI, "0m")