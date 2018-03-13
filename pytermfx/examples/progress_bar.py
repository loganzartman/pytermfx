from pytermfx import Terminal, NamedColor
from pytermfx.tools import draw_progress
from time import sleep

t = Terminal()

def main():
	example_1()
	t.writeln()
	example_2()
	t.writeln()
	example_3()
	t.writeln()
	t.flush()

def example_1():
	color = NamedColor("green")
	progress = 0
	while progress < 1:
		progress += 0.0237
		draw_progress(t, progress, color = color, bar_left = 30,
			label = "Spooling up progress bars...")
		sleep(1/10)

def example_2():
	color = NamedColor("white")
	progress = 0
	while progress < 1:
		progress += 0.0337
		draw_progress(t, progress, color = color, bar_left = 30,
			label = "Computing progress...",
			fill="#", empty="-", head="", format="{0:3.0f}%")
		sleep(1/10)

def example_3():
	color = NamedColor("magenta")
	progress = 0
	while progress < 1:
		progress += 0.0137
		draw_progress(t, progress, color = color, bar_left = 30,
			label = "Installing old program...",
			left="", right="", fill="█", empty="░", head="", 
			format="{0:3.0f}%")
		sleep(1/10)

main() 