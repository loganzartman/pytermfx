from pytermfx import Terminal

t = Terminal()

for i in range(10):
	x, y = t.cursor_get_pos()
	t.cursor_to(x, y + 1)
	t.write(i)
	t.flush()