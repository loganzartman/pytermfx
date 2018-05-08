from pytermfx.constants import *
from pytermfx import Terminal, NamedColor
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
		self.terminal.add_resize_handler(self.update)
		self.eloop = asyncio.get_event_loop()

	def start(self):
		async def readfunc():
			while True:
				c = await self.eloop.run_in_executor(None, self.terminal.getch)
				self.on_input(c)
		self.terminal._handle_resize()
		try:
			self.update()
			self.eloop.run_until_complete(readfunc())
		except KeyboardInterrupt:
			pass
		finally:
			self.terminal.clear()
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

def draw_progress(terminal, progress=0, label="", *, color=NamedColor("white"), 
	              format="{0:.2f}%", left="[", right="]", fill="=", empty=" ",
	              head=">", bar_left=0):
	"""Draw a progress bar.
	terminal - a Terminal instance
	color    - a Color with which to fill the bar
	progress - the progress in range [0, 1]
	"""
	# compute sizes
	percentage = format.format(min(1, max(0, progress)) * 100)
	w = terminal.w
	left_align = max(len(label) + 1, bar_left)
	left_diff = left_align - (len(label) + 1)
	inner_len = w - left_align - 1 - len(left + right) - 1 - len(percentage)
	fill_len = int(inner_len * progress)

	# render progress bar
	terminal.cursor_set_visible(False)
	terminal.clear_line().write(label)
	terminal.write(" " * left_diff, left)
	terminal.style(color)
	terminal.write(fill * (fill_len - len(head))).write(head)
	terminal.write(empty * (inner_len - fill_len))
	terminal.style_reset().write(right, " ", percentage)
	terminal.flush()
	terminal.cursor_set_visible(True)

def draw_hline(terminal, y, ch="═"):
	terminal.cursor_to(0, y)
	terminal.write(ch * terminal.w)
	terminal.flush()

def draw_vline(terminal, x, ch="║"):
	for y in range(terminal.h):
		terminal.cursor_to(x, y)
		terminal.write(ch)
	terminal.flush()