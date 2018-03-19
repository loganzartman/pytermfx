from pytermfx.pytermfx import *
from pytermfx.keys import *

ESC_MAP = {
	"[": {
		"A": KEY_UP,
		"B": KEY_DOWN,
		"C": KEY_RIGHT,
		"D": KEY_LEFT,
		"1": {
			"1": {"~": KEY_F1},
			"2": {"~": KEY_F2},
			"3": {"~": KEY_F3},
			"4": {"~": KEY_F4},
			"5": {"~": KEY_F5},
			"7": {"~": KEY_F6},
			"8": {"~": KEY_F7},
			"9": {"~": KEY_F8}
		},
		"2": {
			"~": KEY_INS,
			"0": {"~": KEY_F9},
			"1": {"~": KEY_F10},
			"3": {"~": KEY_F11},
			"4": {"~": KEY_F12}
		},
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