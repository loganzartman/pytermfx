from pytermfx import Terminal, Style
import sys

t = Terminal()
black = Style.none
white = Style("reverse")

i = 0
for line in sys.stdin:
	for char in line:
		i += 1
		if i % 2 == 0:
			t.style(black)
		else:
			t.style(white)
		t.write(char)
	t.flush()