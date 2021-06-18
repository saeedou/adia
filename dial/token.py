from collections import namedtuple


__all__ = ['Token', 'EXACT_TOKENS']


EOF = 0
NAME = 1
NL = 2
AT = 3
DOT = 4
COLON = 5
LPAR = 6
RPAR = 7
COMA = 8
RARROW = 9
INDENT = 10
DEDENT = 11
BACKSLASH = 12


TOKEN_NAMES = {
    value: name for name, value in globals().items()
    if isinstance(value, int) and not name.startswith('_')
}
__all__.extend(TOKEN_NAMES.values())


EXACT_TOKENS = [
    ('->',  2, RARROW),
    ('@',   1, AT),
    ('.',   1, DOT),
    (':',   1, COLON),
    ('(',   1, LPAR),
    (')',   1, RPAR),
    (',',   1, COMA),
    ('\\',  1, BACKSLASH),
    ('\n',  1, NL),
]


# Token namedtuple
Token = namedtuple('Token', 'type string start end line')
