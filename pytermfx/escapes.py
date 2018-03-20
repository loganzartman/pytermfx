from pytermfx.pytermfx import *
from pytermfx.keys import *

KEY_MAP = {}
KEY_MAP.update({chr(i + 1): Key(chr(97 + i), ctrl=True) for i in range(26)})
del KEY_MAP[chr(9)] # unfortunately ctrl+i is the same as tab and we have no other way
                    # to recognize this.

ESC_MAP = {
	"[": {
		"A": KEY_UP,
		"B": KEY_DOWN,
		"C": KEY_RIGHT,
		"D": KEY_LEFT,
		"a": KEY_UP + MOD_SHIFT,
		"b": KEY_DOWN + MOD_SHIFT,
		"c": KEY_RIGHT + MOD_SHIFT,
		"d": KEY_LEFT + MOD_SHIFT,
		"Z": KEY_TAB + MOD_SHIFT,
		"1": {
			"1": {"~": KEY_F1, "^": KEY_F1 + MOD_CTRL},
			"2": {"~": KEY_F2, "^": KEY_F2 + MOD_CTRL},
			"3": {"~": KEY_F3, "^": KEY_F3 + MOD_CTRL},
			"4": {"~": KEY_F4, "^": KEY_F4 + MOD_CTRL},
			"5": {"~": KEY_F5, "^": KEY_F5 + MOD_CTRL},
			"7": {"~": KEY_F6, "^": KEY_F6 + MOD_CTRL},
			"8": {"~": KEY_F7, "^": KEY_F7 + MOD_CTRL},
			"9": {"~": KEY_F8, "^": KEY_F8 + MOD_CTRL}
		},
		"2": {
			"~": KEY_INS,
			"$": KEY_INS + MOD_SHIFT,
			"^": KEY_INS + MOD_CTRL,
			"@": KEY_INS + MOD_CTRL + MOD_SHIFT,
			"0": {"~": KEY_F9, "^": KEY_F9 + MOD_CTRL},
			"1": {"~": KEY_F10, "^": KEY_F10 + MOD_CTRL},
			"3": {"~": KEY_F11, "^": KEY_F11 + MOD_CTRL},
			"4": {"~": KEY_F12, "^": KEY_F12 + MOD_CTRL}
		},
		"3": {
			"~": KEY_DEL, 
			"$": KEY_DEL + MOD_SHIFT,
			"^": KEY_DEL + MOD_CTRL,
			"@": KEY_DEL + MOD_CTRL + MOD_SHIFT,
		},
		"7": {
			"~": KEY_HOME,
			 "$": KEY_HOME + MOD_SHIFT,
			 "^": KEY_HOME + MOD_CTRL,
			 "@": KEY_HOME + MOD_CTRL + MOD_SHIFT,
		},
		"8": {
			"~": KEY_END,
			 "$": KEY_END + MOD_SHIFT,
			 "^": KEY_END + MOD_CTRL,
			 "@": KEY_END + MOD_CTRL + MOD_SHIFT,
		},
		"5": {
			"~": KEY_PGUP,
			 "$": KEY_PGUP + MOD_SHIFT,
			 "^": KEY_PGUP + MOD_CTRL,
			 "@": KEY_PGUP + MOD_CTRL + MOD_SHIFT,
		},
		"6": {
			"~": KEY_PGDN,
			 "$": KEY_PGDN + MOD_SHIFT,
			 "^": KEY_PGDN + MOD_CTRL,
			 "@": KEY_PGDN + MOD_CTRL + MOD_SHIFT,
		}
	},
	"O": {
		"a": KEY_UP + MOD_CTRL,
		"b": KEY_DOWN + MOD_CTRL,
		"c": KEY_RIGHT + MOD_CTRL,
		"d": KEY_LEFT + MOD_CTRL,
	}
}
ESC_MAP[ESC] = MOD_ALT

def read_escape(file):
	first = file.read(1)
	if first != ESC:
		if first in KEY_MAP:
			return KEY_MAP[first]
		return Key(first)

	mod = MOD_NONE
	skip_once = True
	c = file.read(1)
	c_buffer = []
	m = ESC_MAP

	# special case alt+alpha
	if c not in m:
		if c in KEY_MAP:
			return KEY_MAP[c] + MOD_ALT
		return Key(c) + MOD_ALT

	# iterative case: escape sequence
	while isinstance(m, dict):
		if not skip_once:
			c = file.read(1)
		else:
			skip_once = False
		c_buffer.append(c)
		if c not in m:
			break

		if type(m[c]) == Key:
			return m[c] + mod
		elif type(m[c]) == Mod:
			mod += m[c]
		else:
			m = m[c]

	raise ValueError("Unsupported escape sequence: " + "".join(c_buffer))
