import pytermfx
import time

def main():
	t = pytermfx.Terminal()
	
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

	t.style_fg_256(21)
	t.style_bg_256(231)
	t.style_bold()
	t.clear()

	def update():
		t.clear_box(pos[0]-aw/2, pos[1]-ah/2, aw, ah)

		# integrate velocity
		pos[0] += vel[0]
		pos[1] += vel[1]

		# ugly bounce physics
		if pos[0] < aw/2:
			pos[0] = aw/2
			vel[0] = -vel[0]
		if pos[1] < ah/2+1:
			pos[1] = ah/2+1
			vel[1] = -vel[1]
		if pos[0] > t.w-1-aw/2:
			pos[0] = t.w-1-aw/2
			vel[0] = -vel[0]
		if pos[1] > t.h-1-ah/2:
			pos[1] = t.h-1-ah/2
			vel[1] = -vel[1]

		# update console
		draw_art(t, art, pos[0], pos[1])
		t.flush()

	try:
		while True:
			update()
			time.sleep(1/20)
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