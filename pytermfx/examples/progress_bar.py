from pytermfx import Terminal, NamedColor
from pytermfx.tools import draw_progress
from time import sleep

t = Terminal()

def main():
	example_1()
	t.write("\n")
	example_2()	
	t.flush()

def example_1():
	color = NamedColor("green")
	progress = 0
	while progress < 1:
		progress += 0.0337
		draw_progress(t, color, progress)
		sleep(1/10)

def example_2():
	color = NamedColor("white")
	progress = 0
	while progress < 1:
		progress += 0.0337
		draw_progress(t, color, progress, 
			          fill="#", empty="-", head="", format="{0:3.0f}%")
		sleep(1/10)

main() 