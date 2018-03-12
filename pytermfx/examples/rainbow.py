from pytermfx import Terminal, Color
import pytermfx
import sys
import math
import time

t = Terminal()

def main():
	t.add_resize_handler(update)
	update()
	try:
		while True:
			time.sleep(1/30)
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
	t.flush()

main()