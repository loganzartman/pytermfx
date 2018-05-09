from pytermfx import Terminal, Color, Style
from pytermfx.tools import TerminalApp
from pytermfx.keys import MouseMove
import random
import math

mouse_x = 0
mouse_y = 0
mouse_px = 0
mouse_py = 0
particles = []
t = Terminal()
t.cursor_set_visible(False)
t.set_cbreak(True)
t.mouse_enable("move")
t.style(Color.hex(0)).clear()

class Particle:
	def __init__(self, x, y, vx = 0, vy = 0):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy

	def update(self):
		self.x += self.vx
		self.y += self.vy
		self.vy += 0.1

def update():
	global t, mouse_x, mouse_y, mouse_px, mouse_py
	dx = mouse_x - mouse_px
	dy = mouse_y - mouse_py
	l = math.sqrt(dx ** 2 + dy ** 2)
	d = math.atan2(dy, dx)

	j = min(15, int(l))
	for i in range(j):
		f = i / j
		ll = l* random.uniform(0.25, 0.5)
		dd = d + random.uniform(-0.2, 0.2)
		vx = ll * math.cos(dd)
		vy = ll * math.sin(dd)
		particles.append(Particle(mouse_px + dx * f, mouse_py + dy * f, vx, vy))

	for i, p in enumerate(particles):
		t.cursor_to(int(p.x), int(p.y))
		t.style(Style.none).write(" ")
		p.update()
		if p.x < 0 or p.y < 0 or p.x >= t.w or p.y >= t.h:
			particles.remove(p)
		else:
			t.cursor_to(int(p.x), int(p.y))
			t.style(Color.hsl(i/len(particles), 1.0, 0.5)).write("@")
	t.flush()

	mouse_px = mouse_x
	mouse_py = mouse_y

def on_input(c):
	global mouse_x, mouse_y
	if c == "q":
		app.stop()
	if isinstance(c, MouseMove):
		mouse_x = c.x
		mouse_y = c.y

app = TerminalApp(t, 30, update = update, on_input = on_input)
app.start()