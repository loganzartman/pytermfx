# pytermfx
### Terminal interaction and formatting for Python without curses
---

## Motivation
I originally wanted to create this to help build terminal "screensavers", like [pipes.sh](https://github.com/pipeseroni/pipes.sh) (see my [pipes.py](https://github.com/loganzartman/pytermfx/blob/master/pytermfx/examples/pipes.py)). It might also be useful for things like [progress bars](https://github.com/loganzartman/pytermfx/blob/master/pytermfx/examples/progress_bar.py), or just simple text coloring in the console.

## Installation
Requires Python 3.

`pip install pytermfx`

[pytermfx on PyPI](https://pypi.org/project/pytermfx/)

## Notes
The API is currently unstable. 0.x versions may be incompatible.

## Usage Examples
1. [Creating a Terminal](#creating-a-terminal)
2. [Styling text](#styling-text)
3. [Moving the cursor](#moving-the-cursor)
4. [Clearing the screen](#clearing-the-screen)
5. [Enabling cbreak to accept keyboard input](#enabling-cbreak-to-accept-keyboard-input)
6. [Using input to exit the application](#using-input-to-exit-the-application)
7. [Doing that with TerminalApp](#doing-that-with-terminalapp)

### Creating a Terminal
The `Terminal` class allows you to interact with the terminal emulator.

```python
from pytermfx import Terminal
t = Terminal()

# print the size of the terminal
print("Size: " + t.w + "x" + t.h)

# use pytermfx to print the size of the terminal
t.write("Size: ", t.w, "x", t.h, "\n") # writes are buffered
t.flush()                            # send buffered writes to terminal

# most commands are chainable:
t.write("Hello world!\n").flush() 
```

Q: When should I call flush?

A: Whenever you're done making a set of updates and want them to be displayed on screen.

### Styling text
The `Terminal` instance allows you to format text.

```python
from pytermfx import Terminal
t = Terminal()

# output some bold text
t.style_bold()
t.write("Hello world!\n")
t.style_reset()
t.write("Not bold.\n")
t.flush()

# using print instead
t.style_bold().flush()
print("Hello world!")
```

`Color` and `NamedColor` can be used in combination with the `Terminal` instance to create colors.

```python
from pytermfx import Terminal, Color, NamedColor
t = Terminal()

# output some sky-blue text on a purple background
t.style_fg(Color.hex(0x87CEEB))        # build a color from RGB hex code
t.style_bg(Color.hsl(-0.16, 1.0, 0.5)) # build a color from HSL values
t.write("Sky blue\n")
t.flush()

# output some red text using a named color
t.style_fg(NamedColor("red"))
t.write("Red!\n")
t.flush()
```

Q: What is a "named color"?

A: Different terminals support various kinds of colors. There are three kinds of colors that we can send to terminals:
* 3/4-bit color: 16 different colors with the names "black", "red", "green", "yellow", "blue", "cyan", "magenta", and "white", where each color also has a "bright" variant, e.g. "bright red". The user may change the actual appearance of these colors, for instance, in their `.Xresources` file.
* 8-bit color: A set of 256 colors supported by almost every terminal.
* 24-bit color: True-color; supported only on some terminals.

The `Color` class supports conversion to any of these three. By default, `Terminal` will output 8-bit color. The `NamedColor` class allows you to represent a specific 3/4-bit color instead. See `ColorMode` and `Terminal.set_color_mode()` for more information.

### Moving the cursor
We can use the `Terminal` instance to move the cursor.

```python
from pytermfx import Terminal, Color, NamedColor
t = Terminal()

t.cursor_to(0, 0) # move cursor to the top left of the terminal
t.write("Hey!")   # print some text there
t.flush()

t.cursor_to(14, 1)    # move the cursor to the 15th character of the second line
t.cursor_to_start()   # move the cursor to the start of the second line
t.write("Hey again!") # print some more text
t.flush()
```

### Clearing the screeen
We can use the `Terminal` instance to clear parts of the screen.

```python
from pytermfx import Terminal, Color, NamedColor
t = Terminal()

t.clear()                 # clear the whole screen
t.clear_line()            # clear the current line
t.clear_box(0, 2, t.w, 2) # clear from the start of the third line to the end of the fourth
t.flush()
```

### Enabling cbreak to accept keyboard input
TODO. For now, see `pytermfx/examples/colorwheel.py`

### Using input to exit the application
TODO. For now, see `pytermfx/examples/colorwheel.py`

### Doing that with TerminalApp
TODO. For now, see `pytermfx/examples/dvd.py`
