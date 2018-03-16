from pytermfx import Terminal, VirtualTerminal, Color
from time import sleep
from random import randint

t = Terminal()
vt = VirtualTerminal(t)

vt.write("Testing")
vt.cursor_to(0, 1)
vt.write("Line 2")
vt.refresh()

while True:
	t.cursor_to(randint(0, t.w-1), randint(0, t.h-1))
	t.write("X")
	t.flush()
	sleep(1/1000)