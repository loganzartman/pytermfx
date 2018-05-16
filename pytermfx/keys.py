import unicodedata
from numbers import Number

class Key:
	"""Represents a key and its modifiers.
	"""
	def __init__(self, code=None, name=None, *, ctrl=False, alt=False, shift=False, printable=None):
		assert(code or name)
		# convert character to char code
		if isinstance(code, str):
			code = ord(code)
		
		self.name = name
		self.code = code
		self.ctrl = ctrl
		self.alt = alt
		
		# detect shift key
		if code:
			self.shift = shift or chr(code).isupper()
		else:
			self.shift = shift
		
		# detect printability (non-control)
		if printable == None:
			printable = code and unicodedata.category(chr(code)) != "Cc"
		self.printable = printable
	
	def is_printable(self):
		return self.printable

	def __hash__(self):
		return hash((self.code, self.name, self.ctrl, self.alt, self.shift))

	def __eq__(self, other):
		if isinstance(other, Key):
			return (self.code == other.code and
			        self.name == other.name and
			        self.ctrl == other.ctrl and 
			        self.alt == other.alt and
			        self.shift == other.shift)
		elif isinstance(other, str):
			if other == self.name:
				return True
			if len(other) == 1:
				return Key(other) == self
			return False
		elif isinstance(other, int):
			return self == Key(other)
		else:
			raise RuntimeError("Unsupported type in __eq__: " + type(other))

	def __add__(self, other):
		k = self.clone()
		k += other
		return k

	def __iadd__(self, other):
		if not isinstance(other, Mod):
			raise RuntimeError("Key add only supports Modifier type")
		k = self.clone()
		k.ctrl = self.ctrl or other.ctrl
		k.alt = self.alt or other.alt
		k.shift = self.shift or other.shift
		return k

	def __str__(self):
		if self.code:
			return chr(self.code)
		return ""
	
	def __repr__(self):
		keys = (self.ctrl, self.alt, self.shift, self.name or self.code)
		names = ("ctrl", "alt", "shift", self.name or chr(self.code))
		return "+".join(name for k, name in zip(keys, names) if k)
	
	def clone(self):
		return Key(self.code, self.name, ctrl = self.ctrl, alt = self.alt, shift = self.shift)

class AliasedKeys(Key):
	"""Represents a single key that has multiple key codes.
	For example: backspace and enter on Windows vs POSIX.
	"""
	def __init__(self, *keys, name=None, printable=False):
		self.keys = []
		self.printable = printable
		for key in keys:
			if not isinstance(key, Key):
				key = Key(key, name=name)
			self.keys.append(key)
		self.name = name
	
	def __hash__(self):
		return hash(hash(key) for key in self.keys)
	
	def __eq__(self, other):
		if isinstance(other, str) and other == self.name:
			return True
		return any(key == other for key in self.keys)
	
	def __iadd__(self, other):
		k = self.clone()
		for key in k.keys:
			key += other
		return k
	
	def __str__(self):
		return self.name or self.keys[0].__str__()
	
	def __repr__(self):
		return ", ".join(key.__repr__() for key in self.keys)

	def clone(self):
		return AliasedKeys(self.keys, name=self.name, printable=self.printable)

class Mod(Key):
	"""Represents a modifier key.
	"""
	def __init__(self, ctrl=False, alt=False, shift=False):
		self.key = None
		self.ctrl = ctrl
		self.alt = alt
		self.shift = shift

	def clone(self):
		return Mod(ctrl = self.ctrl, alt = self.alt, shift = self.shift)

class MouseEvent:
	"""Represents a mouse event (click, move, drag, etc.)
	"""
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

	def __str__(self):
		return "mouse"

	def __repr__(self):
		btn_states = zip((self.down, self.up, self.left, self.right), ("down", "up", "left", "right"))
		btn_string = "+".join(name for state, name in btn_states if state)
		return "".join(("mouse ", btn_string, " @ ", str(self.x), ",", str(self.y)))

	def clone(self):
		return MouseEvent(self.x, self.y)

# Key constants
# In general, prefer testing against name or keycode instead of importing these
KEY_UP = Key(name="up")
KEY_DOWN = Key(name="down")
KEY_RIGHT = Key(name="right")
KEY_LEFT = Key(name="left")

KEY_TAB = Key("\t", name="tab")
KEY_BACKSPACE = AliasedKeys(8, 127, name="backspace")
KEY_ENTER = AliasedKeys(10, 13, name="enter")

KEY_ESC = Key(name="escape")
KEY_INS = Key(name="insert")
KEY_DEL = Key(name="delete")
KEY_HOME = Key(name="home")
KEY_END = Key(name="end")
KEY_PGUP = Key(name="pageup")
KEY_PGDN = Key(name="pagedown")

KEY_F1 = Key(name="f1")
KEY_F2 = Key(name="f2")
KEY_F3 = Key(name="f3")
KEY_F4 = Key(name="f4")
KEY_F5 = Key(name="f5")
KEY_F6 = Key(name="f6")
KEY_F7 = Key(name="f7")
KEY_F8 = Key(name="f8")
KEY_F9 = Key(name="f9")
KEY_F10 = Key(name="f10")
KEY_F11 = Key(name="f11")
KEY_F12 = Key(name="f12")

MOD_NONE = Mod()
MOD_CTRL = Mod(ctrl=True)
MOD_ALT = Mod(alt=True)
MOD_SHIFT = Mod(shift=True)
