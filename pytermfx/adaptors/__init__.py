import platform
from pytermfx.adaptors.base import BaseAdaptor
from pytermfx.adaptors.input import InputAdaptor
try:
    import sys
    from pytermfx.adaptors.unix import UnixAdaptor as PlatformAdaptor
except:
    try:
        from ctypes import windll
        winver = int(platform.version().split(".")[0])
        if winver >= 10:
            from pytermfx.adaptors.win32 import Win10Adaptor as PlatformAdaptor
        else:
            from pytermfx.adaptors.win32 import WinNTAdaptor as PlatformAdaptor
    except:
        raise RuntimeError("Platform unsupported.")
