from pytermfx import Terminal, Color

t = Terminal()
t.clear()
adaptor_name = type(t.adaptor).__name__
t.print("Terminal (", adaptor_name, ") ", t.w, "x", t.h, sep="")
t.style(Color.hex(0xFF51C0))
t.print("Hello world in red!")
t.reset()