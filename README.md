# pytermfx
### Terminal interaction and formatting for Python without curses
---

## Motivation
I originally wanted to create this to learn how to build terminal "screensavers", like [pipes.sh](https://github.com/pipeseroni/pipes.sh) (see my [pipes.py](https://github.com/loganzartman/pytermfx/blob/master/pytermfx/examples/pipes.py)). It might also be useful for things like [progress bars](https://github.com/loganzartman/pytermfx/blob/master/pytermfx/examples/progress_bar.py), or just simple text coloring in the console.

## Capabilities
* Cursor movement, screen clearing, etc. (`pytermfx.Terminal`)
* Automatic terminal size detection (`Terminal.w`, `Terminal.h`)
* Text coloring in 256-color or RGB format (`pytermfx.Color`)
* Text styling (`pytermfx.Style`)
* Toggle cbreak mode (`Terminal.set_cbreak()`)
* Keyboard input with support for escape sequences (`pytermfx.Terminal`, `Terminal.getch()`)
	* Read individual key-presses
	* Read arrow keys, function keys, etc.
	* Detect when keys are pressed with modifiers
* Mouse suppport via `getch` with `Terminal.mouse_enable()` and `pytermfx.keys.MouseEvent`
* More

## OS Support
* Supports Unix systems and Windows 10. Good support for most terminal emulators, such as `urxvt`, `st`, `xterm`. Support for Windows before Windows 10 updated console is a work in progess (text styling currently does not work, among other issues).

## Installation
Requires Python 3.

`pip install pytermfx` (version 0.4.2)

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
7. [Using TerminalApp to accept input asynchronously](#using-terminalapp-to-accept-input-asynchronously)

### Creating a Terminal
The `Terminal` class allows you to interact with the terminal emulator.

```python
from pytermfx import Terminal
t = Terminal()

# print the size of the terminal
print("Size: " + t.w + "x" + t.h)

# use pytermfx to print the size of the terminal
t.write("Size: ", t.w, "x", t.h, "\n") # writes are buffered
t.flush()                              # send buffered writes to terminal

# most commands are chainable:
t.writeln("Hello world!").flush() # writeln provides OS-specific newline
t.print("Hello world!")           # works like Python's print() 
```

Q: When should I call flush?

A: Whenever you're done making a set of updates and want them to be displayed on screen.
However, on some platforms (Windows), not flushing does not guarantee that updates will not be displayed.

### Styling text
`Style` in combination with the `Terminal` instance allows you to format text.

```python
from pytermfx import Terminal
t = Terminal()

# output some bold text
t.style(Style("bold"))
t.write("Hello world!\n")
t.style_reset()
t.write("Not bold.\n")
t.flush()

# using print instead
t.style(Style("italic")).flush()
print("Hello world!")
```

`Color` and `NamedColor` can be used in combination with the `Terminal` instance to create colors.

```python
from pytermfx import Terminal, Color, NamedColor
t = Terminal()

# output some sky-blue text on a purple background
t.style(Color.hex(0x87CEEB))             # build a color from RGB hex code
t.style(Color.hsl(-0.16, 1.0, 0.5).bg()) # build a background color from HSL values
t.print("Sky blue")

# output some red text using a named color
t.style(NamedColor("red"))
t.print("Red!")
```

Q: What is a "named color"?

A: Different terminals support various kinds of colors. There are three kinds of colors that we can send to terminals:
* 3/4-bit color: 16 different colors with the names "black", "red", "green", "yellow", "blue", "cyan", "magenta", and "white", where each color also has a "bright" variant, e.g. "bright red". The user may change the actual appearance of these colors, for instance, in their `.Xresources` file.
* 8-bit color: A set of 256 colors supported by almost every terminal.
* 24-bit color: True-color; supported only on some terminals.

The `Color` class supports conversion to any of these three. By default, `Terminal` will output 8-bit color on Unix, and 24-bit color on Windows 10. The `NamedColor` class allows you to represent a specific 3/4-bit color instead. See `ColorMode` and `Terminal.set_color_mode()` for more information.

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

### Clearing the screen
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
To read keypresses as soon as they happen, we need to enable "cbreak" mode (or its Windows equivalent). We should call `reset()` at the end of our program to make sure that the terminal is put back into a usable state before our program exits.

```python
from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)
t.print("Press any key to continue...")
key = t.getch() # wait for keypress
t.print("You pressed:", key)
t.reset()
```

An alternative to manually calling `reset()` is using the `Terminal.managed()` context manager, which also ensures that the terminal is reset even if an error occurs.

```python
from pytermfx import Terminal

t = Terminal()
t.set_cbreak(True)
with t.managed():
    t.print("Press a key.")
    while True:
        t.print("You pressed:", t.getch())
```

See also `pytermfx/examples/colorwheel.py` and `pytermfx/examples/getch.py`

### Using input to exit the application
We can read input in a loop:

```python
from pytermfx import Terminal
from pytermfx.keys import KEY_ESC

t = Terminal()
t.set_cbreak(True)

key = None
while key != KEY_ESC:
    key = t.getch()
    if key == "3":
        t.print("Fizz")
    elif key == "5":
        t.print("Buzz")
t.reset()
```
In this example, pressing the `3` key prints `"Fizz"` and pressing the `5` key prints `"Buzz"`. The program exits when the user presses the `escape` key.

See also `pytermfx/examples/colorwheel.py`

### Using TerminalApp to accept input asynchronously
TODO. For now, see `pytermfx/examples/dvd.py`
