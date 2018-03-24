from pytermfx import Terminal, Color
from pytermfx.keys import MouseMove
from time import clock

t = Terminal()
t.set_cbreak(True)
t.mouse_enable_experimental("move")
t.cursor_set_visible(False)
t.writeln("Left+drag to draw, Right+drag to erase.")
t.writeln("Press C to clear, Q to quit.")
t.flush()

try:
	while True:
		c = t.getch()
		if isinstance(c, MouseMove):
			if c.left:
				t.cursor_to(c.x, c.y)
				t.style(Color.hsl(clock(), 1, 0.7))
				t.write("█").flush()
			elif c.right:
				t.clear_box(c.x - 3, c.y - 1, 6, 3).flush()
		elif c == "c":
			t.clear().flush()
		elif c == "q":
			break
except KeyboardInterrupt:
	pass
finally:
	t.reset()