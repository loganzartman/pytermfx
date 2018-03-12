from pytermfx.pytermfx import *
from pytermfx import Terminal
import asyncio
import sys
import time

class TerminalApp:
	"""A class for managing a terminal app that asynchronously accepts input.
	The client must call start() after constructing the TerminalApp.
	The client may pass an update() parameter to redraw their application.
	The client may pass an on_input(char) parameter to accept a keyboard input.
	"""

	def __init__(self, terminal, **kwargs):
		terminal.set_cbreak(True)
		self.terminal = terminal
		self.on_input = kwargs["on_input"] if "on_input" in kwargs else lambda char: None
		self.update = kwargs["update"] if "update" in kwargs else lambda: None
		self.eloop = asyncio.get_event_loop()

	def start(self):
		def readfunc():
			c = self.terminal.getch()
			self.on_input(c)
			self.update()
		self.eloop.add_reader(sys.stdin.fileno(), readfunc)
		try:
			self.eloop.run_forever()
		except KeyboardInterrupt:
			pass
		finally:
			self.terminal.reset()

class Screensaver(TerminalApp):
	"""An extension of TerminalApp that updates at a fixed rate.
	See TerminalApp for more information.
	"""

	def __init__(self, terminal, framerate, **kwargs):
		super().__init__(terminal, **kwargs)
		self.framerate = framerate
		self.quit_char = kwargs["quit_char"] if "quit_char" in kwargs else "q"
		
		# add exit functionality
		old_input_func = self.on_input
		def input_func(char): 
			self.check_quit(char)
			old_input_func(char)
		self.on_input = input_func

		# set up terminal
		self.terminal.cursor_set_visible(False)
		self.terminal.clear()
		self.terminal.flush()

		# start event loop
		if framerate > 0:
			asyncio.ensure_future(self.redraw_loop(self.update))

	async def redraw_loop(self, update_func):
		while True:
			t0 = time.clock()
			update_func()
			delay = (1 / self.framerate) - (time.clock() - t0)
			await asyncio.sleep(max(0, delay))

	def check_quit(self, char):
		if char == self.quit_char:
			self.eloop.stop()
