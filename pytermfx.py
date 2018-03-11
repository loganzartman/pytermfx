import subprocess
import signal
import sys

ESC = "\x1b"
CSI = ESC + "["
COLOR_256 = 1
COLOR_RGB = 2

class Terminal:
	def __init__(self):
		self._buffer = []
		
		signal.signal(signal.SIGWINCH, self._handle_resize)
		self._resize_handlers = []
		self.add_resize_handler(self.update_size)
		self.update_size()
		
		self._raw = False
		self._cbreak = False
		self._color_mode = COLOR_RGB

	def _handle_resize(self, signum, frame):
		for h in self._resize_handlers:
			h()

	def add_resize_handler(self, func):
		self._resize_handlers.append(func)

	def update_size(self, defaults=None):
		"""Retrieve and store the dimensions of the terminal window.
		Sets self.w and self.h with current data if possible.
		Raises an exception if no size detection method works.
		"""
		try:
			size = subprocess.check_output("stty size", shell=True).split(" ")
			self.w = int(size[0])
			self.h = int(size[1])
			return
		except:
			pass

		try:
			self.w = int(subprocess.check_output("tput cols", shell=True))
			self.h = int(subprocess.check_output("tput lines", shell=True))
			return
		except:
			pass

		if defaults:
			self.w, self.h = defaults
			return
		
		raise RuntimeError("No suitable method to get terminal size.")

	def write(self, *things):
		"""Write an arbitrary number of things to the buffer.
		"""
		self._buffer += map(lambda i: str(i), things)

	def flush(self):
		"""Flush the buffer to the terminal.
		"""
		print("".join(self._buffer), end="")
		sys.stdout.flush()
		self._buffer = []

	def convert_color(self, color):
		"""Converts a given Color to some ANSI format.
		"""
		if self._color_mode == COLOR_256:
			return color.ansi_256()
		if self._color_mode == COLOR_RGB:
			return color.ansi_rgb()
		raise ValueError("_color_mode is invalid.")

	def clear(self):
		"""Clear the screen.
		"""
		self.write(CSI, "2J")

	def clear_box(self, x, y, w, h):
		"""Clears a region of the terminal
		"""
		for i in range(int(y), int(y+h)):
			self.cursor_to(int(x), i)
			self.write(" " * w)

	def reset(self):
		"""Clean up the terminal state before exiting.
		"""
		self.write(ESC, "c") # reset state
		self.cursor_to(0, 0)
		self.clear()
		self.flush()

	def cursor_to(self, x, y):
		"""Move the cursor to an absolute position.
		"""
		self.write(CSI, int(y+1), ";", int(x+1), "H")

	def style_bold(self):
		self.write(CSI, "1m")

	def style_reset(self):
		self.write(CSI, "0m")

	def style_fg(self, col):
		"""Set foreground to a given color
		"""
		self.write(CSI, "38;", self.convert_color(col), "m")

	def style_bg(self, col):
		"""Set background to a given color
		"""
		self.write(CSI, "48;", self.convert_color(col), "m")

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