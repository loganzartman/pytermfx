from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)

try:
	while True:
		s = t.getch_raw()
		codes = [ord(c) for c in s]
		t.print(*codes, sep=", ")
except KeyboardInterrupt:
	pass
finally:
	t.writeln().flush()