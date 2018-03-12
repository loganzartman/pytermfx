from pytermfx import Terminal, Color, ColorMode
import pytermfx
import sys
import math
import time

t = Terminal()
t.set_color_mode(ColorMode.MODE_RGB)

def main():
	t.add_resize_handler(update)
	t.cursor_set_visible(False)
	t.set_cbreak(True)
	update()
	try:
		while t.getch() != "q":
			pass
	except KeyboardInterrupt:
		pass
	finally:
		t.reset()

def update():
	for x in range(t.w):
		for y in range(t.h):
			t.cursor_to(x, y)
			dx = (x/t.w - 0.5) / 0.5
			dy = (y/t.h - 0.5) / 0.5
			a = math.atan2(dy, dx)
			d = math.sqrt(dx ** 2 + dy ** 2)
			t.style_bg(Color.hsl(a / (math.pi * 2), 1.0, 1 - d))
			t.write(" ")
	
	t.cursor_to(1, t.h - 2)
	t.write("Press Q to quit.")

	t.flush()

main()