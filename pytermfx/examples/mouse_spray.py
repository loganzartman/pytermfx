from pytermfx import Terminal, Color, ColorMode
from pytermfx.keys import MouseMove
from pytermfx.tools import Screensaver
from math import sqrt, sin
from random import random

t = Terminal()
t.set_color_mode(ColorMode.MODE_256)
t.set_cbreak(True)
t.cursor_set_visible(False)
t.mouse_enable_experimental("move")
radius = 5 
flow = 0.5
buffer = None
damage = None
mouse = None

def clip(x, lo, hi):
    return max(lo, min(hi, x))

def resize():
	global buffer, damage, t
	buffer = [0 for i in range(t.w * t.h)]
	damage = [True for i in range(t.w * t.h)]
	t.style(Color.hex(0).bg()).clear_box(0, 0, t.w, t.h)
	t.flush()
t.add_resize_handler(resize)
resize()

def spray(cur_x, cur_y, intensity):
	global buffer, damage
	for x in range(cur_x - radius, cur_x + radius + 1):
		for y in range(cur_y - radius // 2, cur_y + radius//2 + 1):
			i = clip(y, 0, t.h-1) * t.w + clip(x, 0, t.w-1)
			dx = x - cur_x
			dy = y - cur_y
			dist = max(0, 1 - sqrt(dx ** 2 + dy ** 2) / radius)
			buffer[i] = min(1, max(0, buffer[i] + dist * intensity * random()))
			damage[i] = True

def draw_buffer():
	global buffer, damage, t
	for y in range(t.h):
		for x in range(t.w):
			i = clip(y, 0, t.h-1) * t.w + clip(x, 0, t.w-1)
			if damage[i]:
				t.cursor_to(x, y)
				v = min(1.0, buffer[i])
				chars = ".'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
				ch = chars[int(v * (len(chars) - 1))]
				# ch = "#"
				t.style(Color.hsl(0.1, 1.0, v*0.6))
				t.write(ch)
				damage[i] = False

def update():
	global mouse, t
	if mouse and (mouse.left or mouse.right):
		spray(mouse.x, mouse.y, flow if mouse.left else -flow)
		draw_buffer()
		t.flush()

def on_input(c):
	global mouse, t
	if isinstance(c, MouseMove):
		mouse = c
	if c == "c":
		resize()
		draw_buffer()
		t.flush()

draw_buffer()
t.flush()
app = Screensaver(t, 30, update = update, on_input = on_input)
app.start()
