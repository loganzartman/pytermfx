from pytermfx import Terminal

if __name__ == "__main__":
	t = Terminal()
	t.set_cbreak(True)
	t.mouse_enable("move")

	with t.managed():
		while True:
			s = t.getch_raw()
			codes = [ord(c) for c in s]
			t.print(*codes, sep=", ")