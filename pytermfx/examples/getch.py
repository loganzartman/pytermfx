from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)
t.write("Last input: ").cursor_save().flush()

try:
	while True:
		c = t.getch()
		t.cursor_restore()
		t.clear_to_end()
		t.write(ord(c))
		t.flush()
except KeyboardInterrupt:
	pass
finally:
	t.writeln().flush()