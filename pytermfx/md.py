"""Parse and render markdown.
"""

from pytermfx import Terminal, Style, NamedColor
from collections import OrderedDict
import re

_style_map = {
	("bold", True): Style("bold"),
	("italic", True): Style("italic"),
	("underline", True): Style("underline"),
	("inline-code", True): NamedColor("light green"),
	("header", 1): (Style("bold", "underline"),),
	("header", 2): (Style("bold", "underline"), NamedColor("light black")),
	("header", 3): (Style("bold"),),
	("header", 4): (Style("bold"),),
	("header", 5): (Style("bold"),),
	("header", 6): (Style("bold"), NamedColor("light black")),
}

def _env_parse_flag(name, *, terminal, match, active_env, i):
	active_env[name] = not active_env[name]
	return i + len(match.group(0))

def _parse_bold(**kwargs):
	return _env_parse_flag("bold", **kwargs)

def _parse_italic(**kwargs):
	return _env_parse_flag("italic", **kwargs)

def _parse_underline(**kwargs):
	return _env_parse_flag("underline", **kwargs)

def _parse_strikethrough(**kwargs):
	return _env_parse_flag("strikethrough", **kwargs)

def _parse_inline_code(**kwargs):
	return _env_parse_flag("inline-code", **kwargs)

def _parse_header(*, terminal, match, active_env, i):
	if match.group(1) == "\n":
		terminal.write("\n\n")

	active_env["header"] = len(match.group(2))
	return i + len(match.group(0))

def _parse_newline(*, terminal, match, active_env, i):
	terminal.write("\n")
	active_env["header"] = 0
	return i + 1

_env_parsers = OrderedDict([
	(r"\*\*",              _parse_bold),          # **bold**
	(r"__",                _parse_underline),     # __underline__
	(r"\*",                _parse_italic),        # *italic*
	(r"_",                 _parse_italic),        # _italic_
	(r"~~",                _parse_strikethrough), # ~~strikethrough~~
	(r"`",                 _parse_inline_code),   # `code`
	(r"(^|\n)(#{1,6})\s*", _parse_header),        # # Header
	(r"\n",                _parse_newline)
])

def render(terminal, s):
	"""Parse and render a markdown string.
	Accepts either a string with newlines, or a list of lines.
	"""
	buf = None
	if isinstance(s, str):
		buf = s
	else:
		buf = "".join(s)

	i = 0
	active_env = {
		"bold": False,
		"italic": False,
		"underline": False,
		"strikethrough": False,
		"inline-code": False,
		"header": 0}

	def apply_style():
		terminal.style(Style.none)
		for env, state in active_env.items():
			if state and (env, state) in _style_map:
				thing = _style_map[(env, state)]
				if hasattr(thing, "__iter__"):
					terminal.style(*thing)
				else:
					terminal.style(thing)

	while i < len(buf):
		matched = False
		for regex, parser in _env_parsers.items():
			match = re.match(regex, buf[i:])
			if match:
				matched = True
				i = parser(terminal = terminal,
				           match = match,
				           active_env = active_env,
				           i = i)
				apply_style()
				break
		if not matched:
			terminal.write(buf[i])
			i += 1