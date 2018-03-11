from pytermfx import Terminal, Color
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
			t.style_bg(Color(x / t.w * 255, y / t.h * 255, x * y / (t.w * t.h) * 255))
			t.write(" ")
	t.flush()

main()