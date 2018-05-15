from pytermfx import Terminal, Color
from pytermfx.tools import TerminalApp
from random import random, randint, choice
from time import sleep

MAX_STEPS = 800
N = 5
TURN_CHANCE = 0.08
CHARS = list("║═╚╝╔╗")
# CHARS = list("│─╰╯╭╮")

t = Terminal()
t.cursor_set_visible(False)
t.add_resize_handler(lambda: t.clear().flush())
i = MAX_STEPS
pipes = []

# choose a connector to use for a given direction
def connector(vx0, vy0, vx1, vy1):
	if vx0 < vx1:
		if vy0 < vy1:
			return CHARS[4]
		return CHARS[2]
	elif vy0 < vy1:
		return CHARS[5]
	return CHARS[3]

class Pipe:
	def __init__(self, x, y, color):
		self.x = x
		self.y = y
		self.color = color

		# choose initial direction
		if random() < 0.5:
			self.vx = choice((-1, 1))
			self.vy = 0
		else:
			self.vy = choice((-1, 1))
			self.vx = 0

	def update(self):
		global t

		old_x, old_y = (self.x, self.y)
		old_vx, old_vy = (self.vx, self.vy)
		
		# turning
		turned = random() < TURN_CHANCE
		if turned:
			if self.vx != 0:
				self.vy = choice((-1, 1))
				self.vx = 0
			elif self.vy != 0:
				self.vx = choice((-1, 1))
				self.vy = 0
		
		# movement
		self.x += self.vx
		self.y += self.vy
		self.wrap()
		
		# prepare to draw pipe
		t.cursor_to(old_x, old_y)
		t.style(self.color)

		# turning
		if turned:
			t.write(connector(old_vx, old_vy, self.vx, self.vy))
		else:
			t.write(CHARS[0] if self.vy != 0 else CHARS[1])
		
	def wrap(self):
		if self.x < 0:
			self.x = t.w - 1
		if self.y < 0:
			self.y = t.h - 1
		if self.x >= t.w:
			self.x = 0
		if self.y >= t.h:
			self.y = 0

def make_pipes(n):
	p = []
	for i in range(n):
		x = randint(0, t.w)
		y = randint(0, t.h)
		color = Color.hsl(random(), 0.5, 0.5)
		p.append(Pipe(x, y, color))
	return p

def update():
	global t, i, pipes
	# reset after fixed interval
	i += 1
	if i > MAX_STEPS:
		t.clear()
		pipes = make_pipes(N)
		i = 0

	# update screen
	for pipe in pipes:
		pipe.update()
	t.flush()

def main():
	def on_input(c):
		if c == "q":
			app.stop()
	app = TerminalApp(t, 60, update=update, on_input=on_input)
	app.start()
	
main()