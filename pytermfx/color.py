from pytermfx.pytermfx import *
import colorsys

class Color:
	def __init__(self, r, g, b):
		"""Construct a color from given r,g,b values.
		Values should be in the range [0, 255]
		"""
		clip = lambda c: int(max(0, min(255, c)))
		self.r = clip(r)
		self.g = clip(g)
		self.b = clip(b)

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

	def ansi_256(self):
		"""Convert this color into ANSI 8-bit color format.
		Red is converted to: "5;196"
		"""
		# grayscale case
		if self.r == self.g == self.b:
			col = 232 + int(self.r / 256 * 24)
			return "5;" + str(col)

		# 216-color RGB
		scale = lambda c: int(c / 256 * 6)
		col = 16
		col += scale(self.b)
		col += scale(self.g) * 6
		col += scale(self.r) * 6 * 6
		return "5;" + str(col)

	def ansi_rgb(self):
		"""Convert this color into ANSI RGB color format.
		Red is converted to: "2;255;0;0"
		"""
		r = str(self.r)
		g = str(self.g)
		b = str(self.b)
		return "".join(("2;", r, ";", g, ";", b))