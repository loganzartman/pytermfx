from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)
t.mouse_enable_experimental("drag")

try:
	while True:
		c = t.getch()
		t.writeln(c.str_long()).flush()
except KeyboardInterrupt:
	pass
finally:
	t.writeln().flush()