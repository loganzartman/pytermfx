from pytermfx.pytermfx import *
from pytermfx.keys import *

KEY_UP = Key("up")
KEY_DOWN = Key("down")
KEY_RIGHT = Key("right")
KEY_LEFT = Key("left")
KEY_INS = Key("insert")
KEY_DEL = Key("delete")
KEY_HOME = Key("home")
KEY_END = Key("end")
KEY_PGUP = Key("pageup")
KEY_PGDN = Key("pagedown")

ESC_MAP = {
	"[": {
		"A": KEY_UP,
		"B": KEY_DOWN,
		"C": KEY_RIGHT,
		"D": KEY_LEFT,
		"2": {"~": KEY_INS},
		"3": {"~": KEY_DEL},
		"7": {"~": KEY_HOME},
		"8": {"~": KEY_END},
		"5": {"~": KEY_PGUP},
		"6": {"~": KEY_PGDN}
	},
}

def read_escape(file):
	first = file.read(1)

	# simple case: literal key
	if first != ESC:
		return Key(first)

	# second case: escape sequence
	c = ""
	c_buffer = []
	m = ESC_MAP
	while isinstance(m, dict):
		c = file.read(1)
		c_buffer.append(c)
		if c not in m:
			break

		if isinstance(m[c], Key):
			return m[c]
		m = m[c]

	raise ValueError("Unsupported escape sequence: " + "".join(c_buffer))