import subprocess
import signal
import sys

CSI = "\x1b["

class Terminal:
	def __init__(self):
		self._buffer = []
		
		signal.signal(signal.SIGWINCH, self._handle_resize)
		self._resize_handlers = []
		self.add_resize_handler(self.update_size)
		self.update_size()
		
		self._raw = False
		self._cbreak = False

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

	def clear(self):
		self.write(CSI, "2J")

	def reset(self):
		self.clear()

	def cursor_to(self, x, y):
		"""Move the cursor
		"""
		self.write(CSI, y, ";", x, "H")