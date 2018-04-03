"""Parse and render markdown.
"""

from pytermfx import Terminal, Style, NamedColor
from collections import OrderedDict
import re

tab_size = 2

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

def _apply_style(terminal, active_env):
	terminal.style(Style.none)
	for env, state in active_env.items():
		if state and (env, state) in _style_map:
			thing = _style_map[(env, state)]
			if hasattr(thing, "__iter__"):
				terminal.style(*thing)
			else:
				terminal.style(thing)

def _env_parse_flag(name, *, terminal, match, active_env, i):
	if name != "inline-code" and active_env["inline-code"]:
		terminal.write(match.group(0))
		return i + 1
	active_env[name] = not active_env[name]
	_apply_style(terminal, active_env)
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

def _render_link(*, terminal, match):
	terminal.style(Style("underline"), NamedColor("light cyan"))
	terminal.write(match.group(1))
	terminal.style(Style.none, NamedColor("cyan"))
	terminal.write(" [", match.group(2), "]")

def _parse_link_ref(*, terminal, match, active_env, i):
	_render_link(terminal=terminal, match=match)
	_apply_style(terminal, active_env)
	return i + len(match.group(0))

def _parse_link_url(*, terminal, match, active_env, i):
	_render_link(terminal=terminal, match=match)
	_apply_style(terminal, active_env)
	return i + len(match.group(0))

def _parse_ref(*, terminal, match, active_env, i):
	terminal.style(NamedColor("cyan"))
	terminal.write(match.group(1),": ")
	terminal.style(Style.none)
	terminal.write(match.group(2))
	_apply_style(terminal, active_env)
	return i + len(match.group(0))

def _parse_code_block(*, terminal, match, active_env, i):
	if match.group(1):
		terminal.style(NamedColor("light green"))
		terminal.write("\n  ", " " * tab_size, match.group(1))
	for line in match.group(2).split("\n"):
		terminal.writeln()
		terminal.style(Style.none)
		terminal.write(" " * tab_size)
		terminal.style(NamedColor("light black").bg()).write(" ")
		terminal.style(Style.none, NamedColor("bright white"))
		terminal.write(" ", line)
	terminal.style(Style.none)
	terminal.write("\n")
	return i + len(match.group(0))

def _parse_header(*, terminal, match, active_env, i):
	if match.group(1) == "\n":
		terminal.write("\n\n")

	active_env["header"] = len(match.group(2))
	_apply_style(terminal, active_env)
	return i + len(match.group(0))

def _parse_li(*, terminal, match, active_env, i):
	level = 0
	if match.group(1):
		level += len(match.group(1)) // 4
	terminal.write("  ");
	terminal.write(" " * (tab_size * level));
	terminal.style(NamedColor("yellow"))
	terminal.write(match.group(2).replace("*", "•").replace("-", "–"))
	_apply_style(terminal, active_env)
	return i + len(match.group(1) or "") + len(match.group(2))

def _parse_newline(*, terminal, match, active_env, i):
	terminal.write("\n")
	active_env["header"] = 0
	_apply_style(terminal, active_env)
	return i + 1

_rc = lambda regex: re.compile(regex, flags=re.MULTILINE) 
_env_parsers = OrderedDict([
	(_rc(r"(^|\n)(#{1,6})\s*"),          _parse_header),        # # Header,
	(_rc(r"^(    *)?(\d+\.) .+$"),       _parse_li),            # 1. numerical list
	(_rc(r"^(    *)?([*+\-]) .+$"),      _parse_li),            # * bulleted list
	(_rc(r"\*\*"),                       _parse_bold),          # **bold**
	(_rc(r"__"),                         _parse_underline),     # __underline__
	(_rc(r"\*"),                         _parse_italic),        # *italic*
	(_rc(r"_"),                          _parse_italic),        # _italic_
	(_rc(r"~~"),                         _parse_strikethrough), # ~~strikethrough~~
	(_rc(r"\[(.+?)\]\[(.+?)\]"),         _parse_link_ref),      # [title][link ref]
	(_rc(r"\[(.+?)\]\((.+?)\)"),         _parse_link_url),      # [title][link url]
	(_rc(r"^\[(.+?)\]: (.+)$"),          _parse_ref),           # [ref]: url
	(_rc(r"```(\w*)\n([\s\S]*?)\n```"),  _parse_code_block),    # ```code```
	(_rc(r"`"),                          _parse_inline_code),   # `code`
	(_rc(r"\n"),                         _parse_newline)
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

	while i < len(buf):
		matched = False
		for regex, parser in _env_parsers.items():
			match = regex.match(buf, i)
			if match:
				matched = True
				i = parser(terminal = terminal,
				           match = match,
				           active_env = active_env,
				           i = i)
				break
		if not matched:
			terminal.write(buf[i])
			i += 1