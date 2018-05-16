from pytermfx import Terminal, NamedColor, Style
from pytermfx.tools import read_line
import os

if __name__ == "__main__":
    t = Terminal()
    
    def update(s):
        for i, word in enumerate(s.split(" ")):
            if i > 0:
                t.write(" ")
            try:
                int(word)
                t.style(NamedColor("red"))
            except:
                pass
            t.write(word).style_reset()

    def autocomplete(word):
        d = os.listdir(os.getcwd())
        matches = [w for w in d if w.startswith(word)]
        return matches[0] if len(matches) > 0 else None

    with t.managed():
        t.print("REPL demo -- a really dumb shell")
        t.print("Filenames in CWD are autocompleted.")
        while True:
            # render prompt
            t.style(NamedColor("yellow"))
            t.write("dumbsh> ")
            t.style_reset().flush()
    
            # read
            s = read_line(t, update, autocomplete)
            
            # eval
            if s == "help":
                # show available commands
                t.print("commands: help, ls, cd, pwd, clear, exit")
            elif s == "ls":
                # list directory contents
                files = os.listdir(os.getcwd())
                t.print(*sorted(files), sep=" ")
            elif s == "pwd":
                # print working directory
                t.print(os.getcwd())
            elif s.startswith("cd"):
                # change working directory
                parts = s.split(" ")
                if len(parts) > 1:
                    path = parts[1]
                    os.chdir(path)
            elif s == "clear":
                # clear the screen
                t.clear()
                t.cursor_to(0, 0)
            elif s == "exit":
                # exit program
                break
            else:
                # echo input
                t.style(Style("italic"))
                t.print(s)
                t.style_reset()
