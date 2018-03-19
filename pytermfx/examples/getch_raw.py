from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)

try:
	while True:
		c = t.getch_raw()
		t.writeln(ord(c)).flush()
except KeyboardInterrupt:
	pass
finally:
	t.writeln().flush()