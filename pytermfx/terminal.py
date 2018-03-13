from pytermfx.pytermfx import *
from pytermfx.color import Color, ColorMode
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
		
		try:
			self._original_attr = termios.tcgetattr(sys.stdin)
		except termios.error:
			self._original_attr = None
		self._cbreak = False
		self._color_mode = ColorMode.MODE_256
		self._cursor_visible = False

	def set_cbreak(self, cbreak=True):
		"""Enable or disable cbreak mode.
		"""
		assert(self._original_attr != None)
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
			raise ValueError("mode must be a ColorMode.")
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

	def getch(self):
		"""Get a single character from stdin in cbreak mode.
		Blocks until the user performs an input. Only works if cbreak is on.
		"""
		if not self._cbreak:
			raise ValueError("Must be in cbreak mode.")
		return sys.stdin.read(1)

	def write(self, *things):
		"""Write an arbitrary number of things to the buffer.
		"""
		self._buffer += map(lambda i: str(i), things)
		return self

	def writeln(self, *things):
		"""Writes an arbitrary number of things to the buffer with a newline.
		"""
		self.write(*things, "\n")
		return self

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
		return self

	def clear_box(self, x, y, w, h):
		"""Clears a region of the terminal
		"""
		for i in range(int(y), int(y+h)):
			self.cursor_to(int(x), i)
			self.write(" " * w)
		return self

	def clear_line(self):
		"""Clear the line and move cursor to start
		"""
		self.cursor_to_start()
		self.write(CSI, "2K")
		return self

	def clear_to_end(self):
		"""Clear to the end of the line
		"""
		self.write(CSI, "0K")
		return self

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
		return self

	def cursor_get_pos(self):
		"""Retrieve the current (x,y) cursor position.
		This is slow, so avoid using when unnecessary.
		"""
		old_status = self._cbreak
		if not self._cbreak:
			self.set_cbreak(True)
		
		# write DSR (device status report)
		self.write(CSI, "6n")
		self.flush()

		# read result from stdin
		buf = []
		while self.getch() != "[": # skip start
			pass
		c = ""
		while c != "R": # read until end
			buf.append(c)
			c = self.getch()
		parts = "".join(buf).split(";")

		# restore old cbreak
		if not old_status:
			self.set_cbreak(False)

		return (int(parts[1]) - 1, int(parts[0]) - 1)

	def cursor_save(self):
		"""Save the cursor position
		"""
		self.write(CSI, "s")
		return self

	def cursor_restore(self):
		"""Restore the cursor position
		"""
		self.write(CSI, "u")
		return self

	def cursor_to(self, x, y):
		"""Move the cursor to an absolute position.
		"""
		self.write(CSI, int(y+1), ";", int(x+1), "H")
		return self

	def cursor_move(self, x, y):
		"""Move the cursor by a given amount.
		"""
		if x < 0:
			self.write(CSI, abs(int(x)), "D")
		elif x > 0:
			self.write(CSI, int(x), "C")
		if y < 0:
			self.write(CSI, abs(int(x)), "A")
		elif y > 0:
			self.write(CSI, int(x), "B")

	def cursor_to_start(self):
		"""Move the cursor to the start of the line.
		"""
		self.write(CSI, "1G")
		return self

	def style(self, style):
		"""Apply a style, which may be a Color or something with .ansi()
		Accepts a Color or a Style.
		"""
		if isinstance(style, Color):
			self.write(style.to_mode(self._color_mode))
		else:
			self.write(style.ansi())
		return self

	def style_reset(self):
		"""Reset style.
		"""
		self.write(CSI, "0m")
		return self
