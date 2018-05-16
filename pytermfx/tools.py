from pytermfx.constants import *
from pytermfx import Terminal, NamedColor
from pytermfx.keys import KEY_BACKSPACE, KEY_TAB, KEY_ENTER
from threading import Thread
import sys
import time


class TerminalApp:
    """A class for managing a terminal app that asynchronously accepts input.
    The client must call start() after constructing the TerminalApp.
    The client may pass an update() parameter to redraw their application.
    The client may pass an on_input(char) parameter to accept a keyboard input.
    """

    def __init__(self, terminal, framerate=0, **kwargs):
        terminal.set_cbreak(True)
        self.terminal = terminal
        self.framerate = framerate
        self.on_input = kwargs["on_input"] if "on_input" in kwargs else lambda char: None
        self.update = kwargs["update"] if "update" in kwargs else lambda: None
        self.terminal.add_resize_handler(self.update)
        self._running = False
        self._threads = []

    def create_thread(self, func):
        t = Thread(target=func)
        self._threads.append(t)
        return t

    def start(self):
        if self._running:
            raise RuntimeError("TerminalApp already running!")

        # create input reader thread
        def readfunc():
            while self._running:
                c = self.terminal.getch()
                try:
                    self.on_input(c)
                except:
                    self.stop()
                    raise
        readthread = self.create_thread(readfunc)

        # create update thread
        def update_loop():
            while self._running:
                t0 = time.process_time()
                try:
                    self.update()
                except:
                    self.stop()
                    raise
                delay = (1 / self.framerate) - (time.process_time() - t0)
                time.sleep(max(0, delay))
        if (self.framerate > 0):
            self.create_thread(update_loop)

        # startup
        self.terminal.clear()
        self.terminal.flush()
        self.terminal._handle_resize()
        self.update()
        self._running = True

        # run threads
        try:
            for t in self._threads:
                t.start()
            readthread.join()
        except KeyboardInterrupt:
            self.stop()

    def stop(self, before_cleanup=lambda: None):
        if not self._running:
            return
        self._running = False
        self._threads = []
        before_cleanup()
        self._cleanup()

    def _cleanup(self):
        self.terminal.cursor_to(0, 0)
        self.terminal.clear()
        self.terminal.flush()
        self.terminal.reset()


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


def print_hcenter(terminal, text, y):
    x = max(0, (terminal.w - len(text)) // 2)
    terminal.cursor_to(x, y)
    terminal.print(text)


def read_line(terminal, update=lambda s: terminal.write(s),
              autocomplete=lambda: None):
    old_status = terminal.adaptor._cbreak
    terminal.set_cbreak(True)
    terminal.cursor_save()

    buffer = []

    def stringify(): return "".join(str(k) for k in buffer)

    def redraw():
        terminal.cursor_restore()
        update(stringify())
        terminal.flush()

    ch = None
    while True:
        ch = terminal.getch()
        if ch == KEY_ENTER:
            break
        elif ch == KEY_BACKSPACE:
            if len(buffer) > 0:
                terminal.cursor_move(-1, 0)
                terminal.write(" ")
                buffer.pop()
        elif ch == KEY_TAB:
            word = stringify().split(" ")[-1]
            candidate = autocomplete(word)
            if candidate is not None:
                buffer = buffer[:-len(word)]
                buffer += candidate
        elif ch.is_printable():
            buffer.append(ch)
        redraw()

    terminal.set_cbreak(old_status)
    terminal.writeln()
    return stringify()
