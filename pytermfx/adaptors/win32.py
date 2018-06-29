from pytermfx.constants import *
from pytermfx.color import Color, ColorMode
from pytermfx.adaptors.base import BaseAdaptor
from pytermfx.adaptors.input import InputAdaptor
from pytermfx.adaptors.vt100 import VT100Adaptor
from threading import Thread
from time import sleep
from ctypes import windll, Structure, byref
from ctypes import c_int, c_short, c_ushort, c_bool, c_wchar, c_uint
import msvcrt

SIZE_POLL_DELAY = 0.2 # terminal size polling interval in seconds
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

def win32_handle(file):
    return msvcrt.get_osfhandle(file.fileno())

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

class Win10Adaptor(InputAdaptor, VT100Adaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler, read_func = self.readch)
        self.in_file = input_file
        self.out_file = output_file
        self.set_color_mode(ColorMode.MODE_RGB)

        # store initial console mode
        self._old_output_mode = c_short()
        kernel32.GetConsoleMode(self.out_handle, byref(self._old_output_mode))
        self._old_input_mode = c_short()
        kernel32.GetConsoleMode(self.in_handle, byref(self._old_input_mode))
        self._old_code_page = kernel32.GetConsoleOutputCP()

        # set console mode
        kernel32.SetConsoleMode(self.out_handle, c_short(WIN10_OUTPUT))
        kernel32.SetConsoleMode(self.in_handle, c_short(WIN10_INPUT_DEFAULT))
        kernel32.SetConsoleOutputCP(65001) # unicode code page

        # poll for resize
        def thread_func():
            while True:
                sleep(SIZE_POLL_DELAY) # must sleep first so terminal initializes
                resize_handler()
        self.resize_thread = Thread(target=thread_func, daemon=True)
        self.resize_thread.start()
    
    @property
    def in_handle(self):
        return win32_handle(self.in_file)
    
    @property
    def out_handle(self):
        return win32_handle(self.out_file)

    def set_cbreak(self, cbreak):
        """Enable or disable cbreak mode.
        """
        if self._cbreak == cbreak:
            return
        
        if cbreak:
            kernel32.SetConsoleMode(self.in_handle, c_short(WIN10_INPUT_CBREAK))
            self._cbreak = True
        else:
            kernel32.SetConsoleMode(self.in_handle, c_short(WIN10_INPUT_DEFAULT))
            self._cbreak = False

    def get_size(self, defaults=None):
        """Retrieve the dimensions of the terminal window.
        Raises an exception if no size detection method works.
        """
        info = CONSOLE_SCREEN_BUFFER_INFO()
        kernel32.GetConsoleScreenBufferInfo(self.out_handle, byref(info))
        w = info.srWindow.Right - info.srWindow.Left
        h = info.srWindow.Bottom - info.srWindow.Top
        return (w+1, h+1)

    def readch(self):
        ch = WCHAR()
        len_read = DWORD()
        kernel32.ReadConsoleW(
            self.in_handle,
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
            self.out_handle,
            msg,
            c_short(len(msg)),
            byref(written),
            None
        )
        self._buffer = []

    def clear(self):
        w, h = self.get_size()
        n_length = w * h
        write_coord = COORD(X=0, Y=0)

        written = DWORD()
        kernel32.FillConsoleOutputAttribute(
            self.out_handle,
            c_short(),
            n_length,
            write_coord,
            byref(written)
        )
        kernel32.FillConsoleOutputCharacterW(
            self.out_handle,
            WCHAR(" "),
            n_length,
            write_coord,
            byref(written)
        )
        self.cursor_to(0, 0)

    def reset(self):
        """Clean up the terminal state before exiting.
        """
        VT100Adaptor.reset(self)
        kernel32.SetConsoleMode(self.out_handle, self._old_output_mode)
        kernel32.SetConsoleMode(self.in_handle, self._old_input_mode)
        kernel32.SetConsoleOutputCP(self._old_code_page)

    def cursor_get_pos(self):
        """Retrieve the current (x,y) cursor position.
        """
        self.flush()
        info = CONSOLE_SCREEN_BUFFER_INFO()
        kernel32.GetConsoleScreenBufferInfo(self.out_handle, byref(info))
        return (info.dwCursorPosition.X, info.dwCursorPosition.Y)

    def cursor_to(self, x, y):
        self.flush()
        pos = COORD(X=x, Y=y)
        kernel32.SetConsoleCursorPosition(self.out_handle, pos)
    
    def cursor_move(self, x, y):
        cur_x, cur_y = self.cursor_get_pos()
        self.cursor_to(cur_x + x, cur_y + y)

class WinNTAdaptor(Win10Adaptor):
    def __init__(self, input_file, output_file, resize_handler=lambda: None):
        super().__init__(input_file, output_file, resize_handler)
        self.in_file = input_file
        self.out_file = output_file
        self.resize_handler = resize_handler
        self.set_color_mode(ColorMode.MODE_16)

        # store initial console mode
        self._old_mode = c_short()
        kernel32.GetConsoleMode(self.out_handle, byref(self._old_mode))

        # set console mode
        out_mode = c_short(ENABLE_PROCESSED_OUTPUT | 
                           ENABLE_WRAP_AT_EOL_OUTPUT)
        kernel32.SetConsoleMode(self.out_handle, out_mode)

    def style(self, *styles):
        pass

    def style_reset(self):
        pass