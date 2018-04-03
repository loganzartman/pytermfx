from pytermfx import Terminal
import pytermfx.md as md
import sys

t = Terminal()

md.render(t, sys.stdin.readlines())
t.flush()
