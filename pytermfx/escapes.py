from pytermfx.constants import *
from pytermfx.keys import *

"""Supports escape sequences for keyboard input.
Be forewarned: this is messy and not portable.
It supports most of the keys I have on my keyboard.
"""


class UnknownEscape(Exception):
    pass


def parse_mouse(seq):
    if len(seq) < 3:
        raise UnknownEscape("Malformed mouse sequence: {}".format(seq))
    btns = ord(seq[0]) - 32
    left = btns & 0b11 == 0b00
    right = btns & 0b11 == 0b10
    moved = btns & 0b100000
    down = not moved and (left or right)
    up = not moved and not (left or right)
    x = ord(seq[1]) - 33
    y = ord(seq[2]) - 33
    return 3, MouseEvent(x, y, left=left, right=right, down=down, up=up, btns=btns)


KEY_MAP = {}
KEY_MAP.update({chr(i + 1): Key(chr(97 + i), ctrl=True) for i in range(26)})
del KEY_MAP[chr(9)]   # fix tab key
del KEY_MAP[chr(10)]  # fix enter key

SEQ_LIST = []  # list of (sequence, key) tuples


def register_seq(seq, key):
    """Register an escape sequence and corresponding Key
    """
    SEQ_LIST.append((seq, key))


def register_seq_mods(seq, key):
    """Register an escape sequence and corresponding Key.
    Include modifier keys.
    """
    register_seq(seq + "~", key)
    register_seq(seq + "$", key + MOD_SHIFT)
    register_seq(seq + "^", key + MOD_CTRL)
    register_seq(seq + "@", key + MOD_CTRL + MOD_SHIFT)


# Misc
register_seq("[M", parse_mouse)
register_seq("[Z", KEY_TAB + MOD_SHIFT)
register_seq("", KEY_ESC)

# Arrow keys
register_seq("[A", KEY_UP)
register_seq("[B", KEY_DOWN)
register_seq("[C", KEY_RIGHT)
register_seq("[D", KEY_LEFT)
register_seq("[a", KEY_UP + MOD_SHIFT)
register_seq("[b", KEY_DOWN + MOD_SHIFT)
register_seq("[c", KEY_RIGHT + MOD_SHIFT)
register_seq("[d", KEY_LEFT + MOD_SHIFT)
register_seq("Oa", KEY_UP + MOD_CTRL)
register_seq("Ob", KEY_DOWN + MOD_CTRL)
register_seq("Oc", KEY_RIGHT + MOD_CTRL)
register_seq("Od", KEY_LEFT + MOD_CTRL)

# Function keys
register_seq_mods("[11", KEY_F1)
register_seq_mods("[12", KEY_F2)
register_seq_mods("[13", KEY_F3)
register_seq_mods("[14", KEY_F4)
register_seq_mods("[15", KEY_F5)
register_seq_mods("[17", KEY_F6)
register_seq_mods("[18", KEY_F7)
register_seq_mods("[19", KEY_F8)
register_seq_mods("[20", KEY_F9)
register_seq_mods("[21", KEY_F10)
register_seq_mods("[23", KEY_F11)
register_seq_mods("[24", KEY_F12)

# Navigation keys
register_seq_mods("[2", KEY_INS)
register_seq_mods("[3", KEY_DEL)
register_seq_mods("[5", KEY_PGUP)
register_seq_mods("[6", KEY_PGDN)
register_seq_mods("[7", KEY_HOME)
register_seq_mods("[8", KEY_END)


def parse_escape(seq, allow_unknown_escapes = True):
    """Parses an escape sequence.
    """
    seq_key = sorted(SEQ_LIST, key=lambda tup: len(tup[0]), reverse=True)
    try:
        while len(seq) > 0:
            # oh look: an ASCII (unicode) character
            first = seq[0]
            if first != ESC:
                if first in KEY_MAP:
                    yield KEY_MAP[first]
                yield Key(first, printable=True)
                seq = seq[1:]
                continue
            
            # an escape sequence
            seq = seq[1:] # strip ESC
            for candidate_seq, val in seq_key:
                if seq.startswith(candidate_seq):
                    seq = seq[len(candidate_seq):]
                    if isinstance(val, Key):
                        yield val
                    elif callable(val):
                        n_remove, result = val(seq)
                        seq = seq[n_remove:]
                        yield result
                    break
            else:
                raise UnknownEscape("Unknown sequence: {}".format(seq))
    except UnknownEscape:
        if allow_unknown_escapes:
            # unrecognized sequence; just dump out raw values
            # anything that checks .is_printable() can ignore these
            for c in seq:
                yield Key(c)
        else:
            raise