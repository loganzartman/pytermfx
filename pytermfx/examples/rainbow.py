from pytermfx import Terminal, Color
import sys

t = Terminal()

i = 0
PERIOD = 500
for line in sys.stdin:
	for char in line:
		i += 1
		t.style(Color.hsl(i / PERIOD, 1.0, 0.6))
		t.write(char)
	t.flush()