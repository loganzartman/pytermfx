from pytermfx import Terminal, Color, Style
from pytermfx.keys import MouseMove
from time import clock

SIZE = 16
old_x = 0
old_y = 0

t = Terminal()
t.set_cbreak(True)
t.mouse_enable_experimental("move")
t.cursor_set_visible(False)
t.clear().flush()

try:
	while True:
		t.style(Style.none)
		t.cursor_to(0,0)
		t.writeln("Hover over terminal")
		t.writeln("Press Q to quit")
		t.flush()

		c = t.getch()
		if isinstance(c, MouseMove):
			t.style(Style.none)
			t.clear_box(old_x - SIZE // 2, old_y - SIZE // 4, SIZE, SIZE // 2)
			t.style(Style("reverse"))
			t.clear_box(c.x - SIZE // 2, c.y - SIZE // 4, SIZE, SIZE // 2)
			old_x = c.x
			old_y = c.y
			t.flush()
		elif c == "q":
			break
except KeyboardInterrupt:
	pass
finally:
	t.reset()