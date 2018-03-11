import pytermfx
import time

def main():
	t = pytermfx.Terminal()
	
	def update():
		t.clear()
		corners = ((0, 0), (t.w - 1, 0), (0, t.h - 1), (t.w - 1, t.h - 1))
		for c in corners:
			t.cursor_to(c[0], c[1])
			t.write("X")
		t.flush()

	t.add_resize_handler(update)
	update()

	try:
		while True:
			time.sleep(1/30)
	except KeyboardInterrupt:
		t.reset()

main()