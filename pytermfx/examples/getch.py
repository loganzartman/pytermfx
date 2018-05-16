from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)
t.mouse_enable("move")

try:
	while True:
		c = t.getch()
		t.writeln(repr(c)).flush()
except KeyboardInterrupt:
	pass
finally:
	t.reset()