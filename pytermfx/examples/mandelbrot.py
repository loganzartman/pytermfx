from pytermfx import Terminal, Color, NamedColor, Style
from pytermfx.tools import TerminalApp

t = Terminal()
t.cursor_set_visible(False)
MAX = 100
STEP = 2
scale = 0.05
off_x = 0
off_y = 0

def mandelbrot(i, j, maxiter):
    real = i
    imag = j
    for n in range(maxiter):
        real2 = real*real
        imag2 = imag*imag
        if real2 + imag2 > 4.0:
            return n
        imag = 2* real*imag + j
        real = real2 - imag2 + i       
    return 0

def color(f):
	return Color.hsl(f / MAX, 1.0, 0.5).bg()

def update():
	# draw mandelbrot
	for y in range(t.h):
		for x in range(t.w):
			cx = (x - t.w / 2) * scale
			cy = (y - t.h / 2) * scale * 2
			t.style(color(mandelbrot(cx + off_x, cy + off_y, MAX)))
			t.write(" ")
		t.cursor_to(0, y)

	# draw info
	t.style(Style("bold"))
	t.style(NamedColor("black")).style(NamedColor("white").bg())
	t.cursor_to(1, 1).writeln("WASD to move")
	t.cursor_to(1, 2).writeln("Q to quit")
	t.style_reset()
	t.flush()

def on_input(char):
	global app, scale, off_x, off_y
	if char == "q":
		app.stop(lambda: t.clear())
		return

	# zoom
	if char == "-":
		scale *= 1.1
	elif char == "=":
		scale /= 1.1
	
	# movement
	if char == "w":
		off_y -= STEP * scale
	elif char == "s":
		off_y += STEP * scale
	elif char == "d":
		off_x += STEP * scale
	elif char == "a":
		off_x -= STEP * scale
	app.update()

app = TerminalApp(t, 0, update = update, on_input = on_input)
app.start()
