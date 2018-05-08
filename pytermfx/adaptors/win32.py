from pytermfx.constants import *
from pytermfx.color import Color, ColorMode
from pytermfx.adaptors.base import BaseAdaptor
from pytermfx.adaptors.vt100 import VT100Adaptor
from pytermfx.escapes import read_escape
from functools import partial
from ctypes import windll, Structure, byref
from ctypes import c_int, c_short, c_ushort, c_bool, c_wchar

kernel32 = windll.kernel32
WORD = c_short
DWORD = c_int
WCHAR = c_wchar

# console input mode flags from wincon.h
ENABLE_ECHO_INPUT = 0x0004
ENABLE_LINE_INPUT = 0x0002
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_INSERT_MODE = 0x0020
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

# console output mode flags
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

# console mode masks
WIN10_INPUT_CBREAK  = ENABLE_VIRTUAL_TERMINAL_INPUT | ENABLE_PROCESSED_INPUT
WIN10_INPUT_DEFAULT = ENABLE_PROCESSED_INPUT | ENABLE_EXTENDED_FLAGS | ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT | ENABLE_QUICK_EDIT_MODE | ENABLE_INSERT_MODE
WIN10_OUTPUT = ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_PROCESSED_OUTPUT

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

class CONSOLE_CURSOR_INFO(Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("bVisible", c_bool)
    ]

class Win10Adaptor(VT100Adaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)
        self.in_file = input_file
        self.out_file = output_file
        self.resize_handler = resize_handler

        # store initial console mode
        self._old_output_mode = c_short()
        kernel32.GetConsoleMode(self.out_file, byref(self._old_output_mode))
        self._old_input_mode = c_short()
        kernel32.GetConsoleMode(self.in_file, byref(self._old_input_mode))

        # set console mode
        kernel32.SetConsoleMode(self.out_file, c_short(WIN10_OUTPUT))
        kernel32.SetConsoleMode(self.in_file, c_short(WIN10_INPUT_DEFAULT))
    
    def set_cbreak(self, cbreak):
        """Enable or disable cbreak mode.
        """
        if self._cbreak == cbreak:
            return self
        
        if cbreak:
            kernel32.SetConsoleMode(self.in_file, c_short(WIN10_INPUT_CBREAK))
            self._cbreak = True
        else:
            kernel32.SetConsoleMode(self.in_file, c_short(WIN10_INPUT_DEFAULT))
            self._cbreak = False
        return self

    def get_size(self, defaults=None):
        """Retrieve the dimensions of the terminal window.
        Raises an exception if no size detection method works.
        """
        info = CONSOLE_SCREEN_BUFFER_INFO()
        kernel32.GetConsoleScreenBufferInfo(self.out_file, byref(info))
        w = info.srWindow.Right - info.srWindow.Left
        h = info.srWindow.Bottom - info.srWindow.Top
        return (w+1, h+1)

    def getch(self):
        """Get a single character from stdin in cbreak mode.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        read_func = partial(Win10Adaptor.getch_raw, self)
        return read_escape(read_func)

    def getch_raw(self):
        """Get a single character from stdin in cbreak mode.
        Does not decode escape sequences.
        Blocks until the user performs an input. Only works if cbreak is on.
        """
        ch = WCHAR()
        len_read = DWORD()
        kernel32.ReadConsoleW(
            self.in_file,
            byref(ch),
            DWORD(1),
            byref(len_read),
            None
        )
        return ch.value

    def flush(self):
        """Flush the buffer to the terminal.
        """
        msg = "".join(self._buffer)
        written = c_short()
        kernel32.WriteConsoleW(
            self.out_file,
            msg,
            c_short(len(msg)),
            byref(written),
            None
        )
        self._buffer = []

    def clear(self):
        w, h = self.get_size()
        written = DWORD()
        kernel32.FillConsoleOutputCharacterW(
            self.out_file,
            WCHAR(" "),
            w * h,
            COORD(X=0, Y=0),
            byref(written)
        )
        self.cursor_to(0, 0)

    def reset(self):
        """Clean up the terminal state before exiting.
        """
        VT100Adaptor.reset(self)
        kernel32.SetConsoleMode(self.out_file, self._old_output_mode)
        kernel32.SetConsoleMode(self.in_file, self._old_input_mode)

    def cursor_get_pos(self):
        """Retrieve the current (x,y) cursor position.
        This is slow, so avoid using when unnecessary.
        """
        self.flush()
        info = CONSOLE_CURSOR_INFO()
        kernel32.GetConsoleCursorInfo(self.out_file, byref(info))
        return (info.dwSize.X, info.dwSize.Y)

    def cursor_to(self, x, y):
        self.flush()
        pos = COORD(X=x, Y=y)
        kernel32.SetConsoleCursorPosition(self.out_file, pos)
        return self

class WinNTAdaptor(Win10Adaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)
        self.in_file = input_file
        self.out_file = output_file
        self.resize_handler = resize_handler

        # store initial console mode
        self._old_mode = c_short()
        kernel32.GetConsoleMode(self.out_file, byref(self._old_mode))

        # set console mode
        out_mode = c_short(ENABLE_PROCESSED_OUTPUT | 
                           ENABLE_WRAP_AT_EOL_OUTPUT)
        kernel32.SetConsoleMode(self.out_file, out_mode)
