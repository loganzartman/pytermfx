from pytermfx.pytermfx import *
from pytermfx.style import *
from pytermfx.color import *
from copy import copy

class VirtualStyle:
	def __init__(self, *styles):
		self.colorfg = NamedColor("white")
		self.colorbg = NamedColor("black", bg=True)
		self.style = Style()
		self.add_styles(styles)

	def add_styles(self, *styles):
		for style in styles:
			if isinstance(style, Style):
				self.style = style
			elif isinstance(style, Color):
				if style._bg:
					self.colorbg = style
				else:
					self.colorfg = style

	def apply_to(self, terminal):
		terminal.style(self.colorfg)
		terminal.style(self.colorbg)
		terminal.style(self.style)

class VirtualChar:
	def __init__(self, value=" ", style=VirtualStyle()):
		self.value = value
		self.style = style
		self.dirty = True

class VirtualTerminal:
	def __init__(self, terminal):
		self.terminal = terminal
		self._cursor = (0, 0)
		self._style = VirtualStyle()
		self._buffer = []
		def resize():
			cols = range(self.terminal.w)
			rows = range(self.terminal.h)
			buffer = [[VirtualChar() for x in cols] for y in rows]
			self._buffer = buffer
		self.terminal.add_resize_handler(resize)
		resize()

	def writech(self, ch):
		# write char
		vch = self._buffer[self._cursor[1]][self._cursor[0]]
		vch.value = ch
		vch.style = copy(self._style)
		vch.dirty = True

		# move cursor
		self._cursor = (self._cursor[0] + 1, self._cursor[1])
		if self._cursor[0] >= self.terminal.w:
			self._cursor = (0, min(self._cursor[1] + 1, self.terminal.h - 1))

	def write(self, *things):
		for thing in things:
			for c in str(thing):
				self.writech(c)

	def cursor_to(self, x, y):
		assert(x >= 0 and y >= 0)
		assert(x < self.terminal.w and y < self.terminal.h)
		self._cursor = (x, y)

	def refresh(self):
		for y in range(self.terminal.h):
			for x in range(self.terminal.w):
				vch = self._buffer[y][x]
				if vch.dirty:
					self.terminal.cursor_to(x, y)
					vch.style.apply_to(self.terminal)
					self.terminal.write(vch.value)
					vch.dirty = False
		self.terminal.flush()

class DisplayManager:
	def __init__(self, terminal):
		self.terminal = terminal

	def add_item(self, drawable):
		pass

	def update(self):
		pass