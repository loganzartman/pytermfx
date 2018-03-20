from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)

try:
	while True:
		c = t.getch()
		t.writeln(c.str_long()).flush()
except KeyboardInterrupt:
	pass
finally:
	t.writeln().flush()