from pytermfx import Terminal

t = Terminal()
adaptor_name = type(t.adaptor).__name__
print("Terminal (", adaptor_name, ") ", t.w, "x", t.h, sep="")