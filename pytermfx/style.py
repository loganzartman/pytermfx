from pytermfx.pytermfx import *

sgr_styles = {
	"reset": 0,
	"bold": 1,
	"faint": 2,
	"italic": 3,
	"underline": 4,
	"slow_blink": 5,
	"fast_blink": 6,
	"reverse": 7,
	"conceal": 8,
	"strikethrough": 9,
	"framed": 51,
	"circled": 52,
	"overlined": 53
}

class Style:
	def __init__(self, *styles):
		self.styles = set()
		for s in styles:
			self.add(s)

	def add(self, style):
		assert(style in sgr_styles)
		self.styles.add(sgr_styles[style])

	def remove(self, style):
		self.styles.remove(sgr_styles[style])

	def clear(self):
		self.styles = set()

	def ansi(self):
		output = "".join(CSI + str(s) + "m" for s in self.styles)
		return "".join((CSI, "0m", output))