from pytermfx.pytermfx import *
from pytermfx.color import ColorMode
import subprocess
import signal
import sys
import termios
import tty

class Terminal:
	def __init__(self):
		self._buffer = []
		
		signal.signal(signal.SIGWINCH, self._handle_resize)
		self._resize_handlers = []
		self.add_resize_handler(self.update_size)
		self.update_size()
		
		self._original_attr = termios.tcgetattr(sys.stdin)
		self._cbreak = False
		self._color_mode = ColorMode.MODE_256
		self._cursor_visible = False

	def set_cbreak(self, cbreak=True):
		"""Enable or disable cbreak mode.
		"""
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._original_attr)
		if cbreak:
			tty.setcbreak(sys.stdin.fileno())
		self._cbreak = cbreak

	def set_color_mode(self, mode):
		"""Change the color mode of the terminal.
		The color mode determines what kind of ANSI sequences are used to
		set colors. See ColorMode for more details.
		"""
		if not isinstance(mode, ColorMode):
			raise ArgumentError("mode must be a ColorMode.")
		self._color_mode = mode

	def _handle_resize(self, signum, frame):
		for h in self._resize_handlers:
			h()

	def add_resize_handler(self, func):
		"""Adds a handler for terminal resize.
		"""
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

	def cursor_set_visible(self, visible=True):
		"""Change the cursor visibility.
		visible may be True or False.
		"""
		self.write(CSI, "?25", "h" if visible else "l")
		self._cursor_visible = visible

	def cursor_to(self, x, y):
		"""Move the cursor to an absolute position.
		"""
		self.write(CSI, int(y+1), ";", int(x+1), "H")

	def style_bold(self):
		"""Enable bold style.
		"""
		self.write(CSI, "1m")

	def style_reset(self):
		"""Reset style.
		"""
		self.write(CSI, "0m")

	def style_fg(self, col):
		"""Set foreground to a given color
		"""
		self.write(CSI, col.to_mode(self._color_mode, bg=False), "m")

	def style_bg(self, col):
		"""Set background to a given color
		"""
		self.write(CSI, col.to_mode(self._color_mode, bg=True), "m")