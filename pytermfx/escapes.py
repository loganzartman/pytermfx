from pytermfx.constants import *
from pytermfx.keys import *

"""Supports escape sequences for keyboard input.
Be forewarned: this is messy and not portable.
It supports most of the keys I have on my keyboard.
"""

KEY_MAP = {}
SEQ_LIST = []  # list of (sequence, key) tuples

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

def parse_esc_key(seq):
    if len(seq) > 1:
        # detect unrecognized escape sequence and remove it
        return len(seq), None
    return 1, KEY_ESC

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
                else:
                    yield Key(first)
                seq = seq[1:]
                continue
            
            # special case for alt+key
            # does not currently support all alt+key combos
            if len(seq) == 2:
                # note that this will fail to detect alt+key for simultaneous
                # keypresses, but I don't think we can solve this.
                key = seq[1]
                if ord(key) < 127:
                    if key in KEY_MAP:
                        yield KEY_MAP[key] + MOD_ALT
                    else:
                        yield Key(key, alt=True)
                    break
            
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
                        if result is not None:
                            yield result
                    break
            else:
                raise UnknownEscape("Unknown sequence: {}".format(seq))
    except UnknownEscape:
        if not allow_unknown_escapes:
            # unrecognized sequence
            raise

def register_seq(*seq, val):
    """Register an escape sequence and corresponding Key
    """
    for s in seq:
        SEQ_LIST.append((s, val))


def register_seq_mods(*seq, val):
    """Register an escape sequence and corresponding Key.
    Include modifier keys.
    """
    add_each = lambda i, v: [x + v for x in i]
    register_seq(*add_each(seq, "~"), val = val)
    register_seq(*add_each(seq, "$"), val = val + MOD_SHIFT)
    register_seq(*add_each(seq, "^"), val = val + MOD_CTRL)
    register_seq(*add_each(seq, "@"), val = val + MOD_CTRL + MOD_SHIFT)

# Build key map
KEY_MAP.update({chr(i + 1): Key(chr(97 + i), ctrl=True) for i in range(26)})
KEY_MAP["\t"] = KEY_TAB
KEY_MAP[chr(8)] = KEY_BACKSPACE
KEY_MAP[chr(127)] = KEY_BACKSPACE
KEY_MAP[chr(10)] = KEY_ENTER
KEY_MAP[chr(13)] = KEY_ENTER

# Register escape sequences
# Misc
register_seq("[M", val = parse_mouse)
register_seq("[Z", val = KEY_TAB + MOD_SHIFT)
register_seq("", val = parse_esc_key)

# Arrow keys
register_seq("[A", val = KEY_UP)
register_seq("[B", val = KEY_DOWN)
register_seq("[C", val = KEY_RIGHT)
register_seq("[D", val = KEY_LEFT)
register_seq("[a", val = KEY_UP + MOD_SHIFT)
register_seq("[b", val = KEY_DOWN + MOD_SHIFT)
register_seq("[c", val = KEY_RIGHT + MOD_SHIFT)
register_seq("[d", val = KEY_LEFT + MOD_SHIFT)
register_seq("Oa", val = KEY_UP + MOD_CTRL)
register_seq("Ob", val = KEY_DOWN + MOD_CTRL)
register_seq("Oc", val = KEY_RIGHT + MOD_CTRL)
register_seq("Od", val = KEY_LEFT + MOD_CTRL)

# Function keys
register_seq_mods("[11", val = KEY_F1)
register_seq_mods("[12", val = KEY_F2)
register_seq_mods("[13", val = KEY_F3)
register_seq_mods("[14", val = KEY_F4)
register_seq("OP", val = KEY_F1)
register_seq("OQ", val = KEY_F2)
register_seq("OR", val = KEY_F3)
register_seq("OS", val = KEY_F4)
register_seq_mods("[15", val = KEY_F5)
register_seq_mods("[17", val = KEY_F6)
register_seq_mods("[18", val = KEY_F7)
register_seq_mods("[19", val = KEY_F8)
register_seq_mods("[20", val = KEY_F9)
register_seq_mods("[21", val = KEY_F10)
register_seq_mods("[23", val = KEY_F11)
register_seq_mods("[24", val = KEY_F12)

# Navigation keys
register_seq_mods("[2", val = KEY_INS)
register_seq_mods("[3", val = KEY_DEL)
register_seq_mods("[5", val = KEY_PGUP)
register_seq_mods("[6", val = KEY_PGDN)
register_seq("[H", val = KEY_PGUP)
register_seq("[F", val = KEY_PGDN)
register_seq_mods("[7", val = KEY_HOME)
register_seq_mods("[8", val = KEY_END)
