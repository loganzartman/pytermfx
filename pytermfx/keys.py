from numbers import Number
import os

class Key:
	def __init__(self, key, ctrl=False, alt=False, shift=False, printable=False):
		if isinstance(key, int):
			key = chr(key)
		self.key = key.lower()
		self.ctrl = ctrl
		self.alt = alt
		self.shift = shift or key.isupper()
		self.printable = printable
	
	def char(self):
		return self.key.upper() if self.shift else self.key
	
	def is_printable(self):
		return self.printable

	def __hash__(self):
		return hash((self.key, self.ctrl, self.alt, self.shift))

	def __eq__(self, other):
		if isinstance(other, Key):
			return (self.key == other.key and
			       self.ctrl == other.ctrl and 
			       self.alt == other.alt and
			       self.shift == other.shift)
		elif isinstance(other, str):
			return self == Key(other)
		elif isinstance(other, int):
			return self == Key(chr(other))
		else:
			return NotImplemented

	def __add__(self, other):
		k = self.clone()
		k += other
		return k

	def __iadd__(self, other):
		if not isinstance(other, Mod):
			return NotImplemented
		k = self.clone()
		k.ctrl = self.ctrl or other.ctrl
		k.alt = self.alt or other.alt
		k.shift = self.shift or other.shift
		return k

	def __str__(self):
		return self.key.upper() if self.shift else self.key

	def str_long(self):
		keys = (self.ctrl, self.alt, self.shift, self.key)
		names = ("ctrl", "alt", "shift", self.key)
		return "+".join(name for k, name in zip(keys, names) if k)

	def clone(self):
		return Key(self.key, ctrl = self.ctrl, alt = self.alt, shift = self.shift)

class AliasedKeys(Key):
	def __init__(self, *keys, printable=False):
		self.keys = []
		self.printable = printable
		for key in keys:
			if not isinstance(key, Key):
				key = Key(key)
			self.keys.append(key)
	
	def char(self):
		return self.keys[0].char()
	
	def __hash__(self):
		return hash(hash(key) for key in self.keys)
	
	def __eq__(self, other):
		return any(key == other for key in self.keys)
	
	def __iadd__(self, other):
		k = self.clone()
		for key in k.keys:
			key += other
		return k
	
	def str_long(self):
		return ", ".join(key.str_long() for key in self.keys)

	def clone(self):
		return AliasedKeys(self.keys)

KEY_UP = Key("up")
KEY_DOWN = Key("down")
KEY_RIGHT = Key("right")
KEY_LEFT = Key("left")

KEY_TAB = Key("\t")
KEY_BACKSPACE = AliasedKeys(8, 127)
KEY_ENTER = Key(os.linesep)

KEY_ESC = Key("escape")
KEY_INS = Key("insert")
KEY_DEL = Key("delete")
KEY_HOME = Key("home")
KEY_END = Key("end")
KEY_PGUP = Key("pageup")
KEY_PGDN = Key("pagedown")

KEY_F1 = Key("f1")
KEY_F2 = Key("f2")
KEY_F3 = Key("f3")
KEY_F4 = Key("f4")
KEY_F5 = Key("f5")
KEY_F6 = Key("f6")
KEY_F7 = Key("f7")
KEY_F8 = Key("f8")
KEY_F9 = Key("f9")
KEY_F10 = Key("f10")
KEY_F11 = Key("f11")
KEY_F12 = Key("f12")

class Mod(Key):
	def __init__(self, ctrl=False, alt=False, shift=False):
		self.key = None
		self.ctrl = ctrl
		self.alt = alt
		self.shift = shift

	def clone(self):
		return Mod(ctrl = self.ctrl, alt = self.alt, shift = self.shift)

MOD_NONE = Mod()
MOD_CTRL = Mod(ctrl=True)
MOD_ALT = Mod(alt=True)
MOD_SHIFT = Mod(shift=True)

class MouseEvent:
	def __init__(self, x, y, *, left = False, right = False, down = False, up = False, btns = 0):
		self.x = x
		self.y = y
		self.left = left
		self.right = right
		self.down = down
		self.up = up
		self.btns = btns
	
	def is_printable(self):
		return False

	def str_long(self):
		btn_states = zip((self.down, self.up, self.left, self.right), ("down", "up", "left", "right"))
		btn_string = "+".join(name for state, name in btn_states if state)
		return "".join(("mouse ", btn_string, " @ ", str(self.x), ",", str(self.y)))

	def clone(self):
		return MouseEvent(self.x, self.y)