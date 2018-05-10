from pytermfx import Terminal, Color, Style
from pytermfx.keys import MouseEvent
from time import clock

BASE_SIZE = 4
MAX_SIZE = BASE_SIZE * 3
old_x = 0
old_y = 0

t = Terminal()
t.set_cbreak(True)
t.mouse_enable("move")
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
		if isinstance(c, MouseEvent):
			if c.down:
				size = BASE_SIZE * 3
			elif c.left or c.right:
				size = BASE_SIZE * 2
			else:
				size = BASE_SIZE 

			t.style(Style.none)
			t.clear_box(old_x - MAX_SIZE // 2, old_y - MAX_SIZE // 4, MAX_SIZE, MAX_SIZE // 2)
			
			if c.left:
				t.style(Color.hex(0xFF0000).bg())
			elif c.right:
				t.style(Color.hex(0x00FF00).bg())
			else:
				t.style(Style("reverse"))
			t.clear_box(c.x - size // 2, c.y - size // 4, size, size // 2)
			
			old_x = c.x
			old_y = c.y
			t.flush()
		elif c == "q":
			break
except KeyboardInterrupt:
	pass
finally:
	t.reset()