from numbers import Number

class Key:
	def __init__(self, key, ctrl=False, alt=False, shift=False):
		self.key = key.lower()
		self.ctrl = ctrl
		self.alt = alt
		self.shift = shift or key.isupper()

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
		k = Key(self.key, ctrl = self.ctrl, alt = self.alt, shift = self.shift)
		k += other
		return k

	def __iadd__(self, other):
		if not isinstance(other, Mod):
			return NotImplemented
		self.ctrl = self.ctrl or other.ctrl
		self.alt = self.alt or other.alt
		self.shift = self.shift or other.shift
		return self

	def __str__(self):
		return self.key.upper() if self.shift else self.key

class Mod(Key):
	def __init__(self, ctrl=False, alt=False, shift=False):
		self.key = None
		self.ctrl = ctrl
		self.alt = alt
		self.shift = shift

MOD_CTRL = Mod(ctrl=True)
MOD_ALT = Mod(alt=True)
MOD_SHIFT = Mod(shift=True)