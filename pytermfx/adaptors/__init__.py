import platform
from pytermfx.adaptors.base import BaseAdaptor
try:
    import sys
    STDIN = sys.stdin
    STDOUT = sys.stdout
    from pytermfx.adaptors.unix import UnixAdaptor as PlatformAdaptor
except:
    try:
        from ctypes import windll
        STDIN = windll.kernel32.GetStdHandle(-10)
        STDOUT = windll.kernel32.GetStdHandle(-11)
        winver = int(platform.version().split(".")[0])
        if winver >= 10:
            from pytermfx.adaptors.win32 import Win10Adaptor as PlatformAdaptor
        else:
            from pytermfx.adaptors.win32 import WinNTAdaptor as PlatformAdaptor
    except:
        raise RuntimeError("Platform unsupported.")
