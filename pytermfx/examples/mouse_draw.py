from pytermfx import Terminal, Color
from pytermfx.keys import MouseMove
from time import clock

t = Terminal()
t.set_cbreak(True)
t.mouse_enable_experimental("drag")
t.writeln("Click and drag to draw")
t.writeln("Press C to clear")
t.writeln("Press Q to quit")
t.flush()

try:
	while True:
		c = t.getch()
		if isinstance(c, MouseMove):
			t.cursor_to(c.x, c.y)
			t.style(Color.hsl(clock(), 1, 0.7))
			t.write("█").flush()
		elif c == "c":
			t.clear().flush()
		elif c == "q":
			break
except KeyboardInterrupt:
	pass
finally:
	t.reset()