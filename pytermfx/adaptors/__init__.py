from pytermfx.adaptors.base import BaseAdaptor
try:
    from pytermfx.adaptors.vt100 import VT100Adaptor as PlatformAdaptor
    import sys
    STDIN = sys.stdin
    STDOUT = sys.stdout
except:
    try:
        from pytermfx.adaptors.win32 import Win32Adaptor as PlatformAdaptor
        from ctypes import windll
        STDIN = windll.kernel32.GetStdHandle(-10)
        STDOUT = windll.kernel32.GetStdHandle(-11)
    except:
        raise RuntimeError("Platform unsupported.")
