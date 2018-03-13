from pytermfx.pytermfx import *
from enum import Enum
import colorsys
import math

class ColorMode(Enum):
	"""Represents the various types of ANSI escapes that set colors.
	All modes other than MODE_RGB will approximate RGB colors with varying
	degrees of accuracy. Terminal uses MODE_256 by default because most 
	emulators support it, but many do not support 24-bit color.
	MODE_16  - 3/4 bit color (named colors)
	MODE_256 - 8 bit color
	MODE_RGB - 24 bit color
	"""
	MODE_16  = 0
	MODE_256 = 1
	MODE_RGB = 2

class Color:
	def __init__(self, r, g, b, bg=False):
		"""Construct a color from given r,g,b values.
		Values should be in the range [0, 255]
		"""
		clip = lambda c: int(max(0, min(255, c)))
		self.r = clip(r)
		self.g = clip(g)
		self.b = clip(b)
		self._bg = bg

	def bg(self):
		"""Make this a background color.
		"""
		self._bg = True
		return self

	def fg(self):
		"""Make this a foreground color.
		"""
		self._bg = False
		return self

	@staticmethod
	def hex(hex):
		"""Construct a color from a given hex value.
		Red is: 0xFF0000
		"""
		return Color(
			(hex >> 16) & 0xFF,
			(hex >>  8) & 0xFF,
			 hex        & 0xFF)

	@staticmethod
	def rgb(r, g, b):
		return Color(r * 255, g * 255, b * 255)

	@staticmethod
	def hsl(h, s, l):
		r, g, b = colorsys.hls_to_rgb(h, l, s)
		return Color.rgb(r, g, b)

	def to_mode(self, color_mode):
		"""Output a string in a given ANSI color format.
		"""
		if color_mode == ColorMode.MODE_16:
			return self.ansi_16()
		if color_mode == ColorMode.MODE_256:
			return self.ansi_256()
		if color_mode == ColorMode.MODE_RGB:
			return self.ansi_rgb()
		raise ValueError("color_mode is invalid. Should be a ColorMode enum.")

	def ansi_16(self):
		"""Convert this color into ANSI 3/4-bit color format.
		Red foreground is converted to: "91"
		This converter is slow and inaccurate.
		"""
		# list of named ANSI colors and xterm color values
		colors = ((0,0,0), (205,0,0), (0,205,0), (205,205,0),
			(0,0,238), (205,0,205), (0,205,205), (229,229,229),
			(127,127,127), (255,0,0), (0,255,0), (255,255,0),
			(92,92,255), (255,0,255), (0,255,255), (255,255,255))
		ids = list(range(0, 8)) + list(range(60, 68))

		def dist(a, b):
			return math.sqrt(
				(a[0] - b[0]) ** 2 + 
				(a[1] - b[1]) ** 2 + 
				(a[2] - b[2]) ** 2)

		# find closest (euclidean) named color (xterm defaults) to input
		own_col = (self.r, self.g, self.b)
		min_i = 0
		for i, col in enumerate(colors):
			if dist(colors[i], own_col) < dist(colors[min_i], own_col):
				min_i = i
		return CSI + str((40 if self._bg else 30) + ids[min_i]) + "m"

	def ansi_256(self):
		"""Convert this color into ANSI 8-bit color format.
		Red foreground is converted to: "38;5;196"
		This converter emits the 216 RGB colors and the 24 grayscale colors.
		It does not use the 16 named colors.
		"""
		if self.r == self.g == self.b:
			# grayscale case
			col = 232 + int(self.r / 256 * 24)
		else:
			# 216-color RGB
			scale = lambda c: int(c / 256 * 6)
			col = 16
			col += scale(self.b)
			col += scale(self.g) * 6
			col += scale(self.r) * 6 * 6
		return CSI + ("48;5;" if self._bg else "38;5;") + str(col) + "m"

	def ansi_rgb(self):
		"""Convert this color into ANSI RGB color format.
		Red foreground is converted to: "38;2;255;0;0"
		"""
		r = str(self.r)
		g = str(self.g)
		b = str(self.b)
		esc = ("48;2;" if self._bg else "38;2;")
		return "".join((CSI, esc, r, ";", g, ";", b)) + "m"

class NamedColor(Color):
	"""Implements a color that is always one of the 16 named colors.
	"""
	def __init__(self, name_or_id, bg=False):
		if name_or_id in range(0, 16):
			self.id = name_or_id
		else:
			try:
				id = NamedColor.name_to_id(name_or_id)
			except ValueError:
				raise ValueError("name_or_id must be an integer ID in [0, 15] "
					+ "or a color name.")
			self.id = id
		self._bg = bg

	@staticmethod
	def name_to_id(name):
		names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
		names_bright = ["bright" + name for name in names]
		target = name.lower().replace(" ", "").replace("_", "").replace("light", "bright")
		try:
			return names.index(target)
		except ValueError:
			return names_bright.index(target) + 60

	def ansi_16(self):
		return CSI + str(self.id + (40 if self._bg else 30)) + "m"

	def ansi_256(self, **kwargs):
		return self.ansi_16(**kwargs)

	def ansi_rgb(self, **kwargs):
		return self.ansi_16(**kwargs)