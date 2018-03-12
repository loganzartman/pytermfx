from pytermfx import Terminal, Color
import time
import random

def main():
	t = Terminal()
	t.cursor_set_visible(False)
	
	# the beautiful art
	art = [
		"DDDDDDDDDVVVVVV        VVVVDDDDDDDDDD   ",
		"DDDDDDDDDDDVVVVV      VVVVVDDDDDDDDDDDD ",
		"        DDDD VVVV    VVVV           DDDD",
		"DDD      DDD  VVVV  VVVV    DDD      DDD",
		"DDD     DDDD   VVVVVVVV     DDD     DDDD",
		"DDDDDDDDDDD     VVVVVV      DDDDDDDDDDD ",
		"DDDDDDDDD        VVVV       DDDDDDDDD   ",
		"                  VV                    "
	]
	aw = len(art[0])
	ah = len(art)
	pos = [t.w/2, t.h/2]
	vel = [1.12, 0.67]

	t.style_fg(Color.hex(0x0000FF))
	t.style_bg(Color.hex(0x000000))
	t.style_bold()
	t.clear()

	def changecol():
		colors = (
			Color.hex(0x0000FF),
			Color.hex(0xFFFF00),
			Color.hex(0x7700FF),
			Color.hex(0xFF0077),
			Color.hex(0xFF7700))
		t.style_fg(random.choice(colors))

	def update():
		t.clear_box(pos[0]-aw/2, pos[1]-ah/2, aw, ah)

		# integrate velocity
		pos[0] += vel[0]
		pos[1] += vel[1]

		# ugly bounce physics
		if pos[0] < aw/2:
			pos[0] = aw/2
			vel[0] = -vel[0]
			changecol()
		if pos[1] < ah/2+1:
			pos[1] = ah/2+1
			vel[1] = -vel[1]
			changecol()
		if pos[0] > t.w-1-aw/2:
			pos[0] = t.w-1-aw/2
			vel[0] = -vel[0]
			changecol()
		if pos[1] > t.h-1-ah/2:
			pos[1] = t.h-1-ah/2
			vel[1] = -vel[1]
			changecol()

		# update console
		draw_art(t, art, pos[0], pos[1])
		t.flush()

	try:
		while True:
			update()
			time.sleep(1/30)
	except KeyboardInterrupt:
		t.reset()

def draw_art(term, art, x, y):
	w = len(art[0])
	h = len(art)
	x0 = int(x - w/2)
	y0 = int(y - h/2)
	for y in range(len(art)):
		term.cursor_to(x0, y0+y)
		term.write(art[y])

main()