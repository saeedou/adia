import io
import re

from .token import *
from .token import EXACT_TOKENS, Token


# Regex patterns
WHITESPACE_RE = r' +'
NAME_RE = r'\w+'
NEWLINE_RE = re.escape('\n')
ALLTOKENS_RE = \
    [re.escape(i[0]) for i in EXACT_TOKENS] + \
    [WHITESPACE_RE, NAME_RE, NEWLINE_RE]
ALLTOKENS_RE = re.compile('(' + '|'.join(ALLTOKENS_RE) + ')')
TOKENS_DICT = {t: n for t, n in EXACT_TOKENS}


class Tokenizer:
    def __init__(self):
        self.filename = "String"
        self.lineno = 0
        self.coloffset = -1
        self.indentsize = 0
        self.indent = 0
        self.escape = False
        self.newline = True
        self._mlmatch = []
        self._ml = False
        self._mlindent = False
        self._mllastlen = 0

    def _token(self, type_, string, start, end, line):
        return Token(
            type_,
            string,
            (self.lineno, start),
            (self.lineno, end),
            line
        )

    def _eoftoken(self, line):
        return Token(EOF, '', (self.lineno, 0), (self.lineno, 0), '')

    def _indenttoken(self, token, start, end, line):
        return Token(
            INDENT,
            token[self.coloffset:],
            (self.lineno, start + self.coloffset),
            (self.lineno, end),
            line
        )

    def _dedenttoken(self, lineindent, line):
        return Token(
            DEDENT, '',
            (self.lineno, lineindent * self.indentsize + self.coloffset),
            (self.lineno, lineindent * self.indentsize + self.coloffset),
            line
        )

    def _newlinetoken(self, token, start, end, line):
        return Token(
            NEWLINE,
            token,
            (self.lineno, start),
            (self.lineno, end),
            line
        )

    def _everything(self, start, line):
        end = len(line)
        value = line[start:-1]

        yield Token(
            EVERYTHING,
            value,
            (self.lineno, start),
            (self.lineno, end - 1),
            line
        )

        yield self._newlinetoken(line[-1], end - 1, end, line)

    def _tokenizeline(self, line):
        self.lineno += 1

        if self._ml:
            m = re.match(WHITESPACE_RE, line)
            end = m.span()[1] if m else 0
            if self._mlindent == 0 and end > 0:
                self._mlindent = end
                self._mltoken = line[self._mlindent:]
                self._mllastlen = len(line)
                return
            elif end < self._mlindent:
                sl = self._mlmatch[-1].start[0]
                self._mlmatch.clear()
                yield Token(
                    MULTILINE,
                    self._mltoken[:-1],
                    (sl + 1, self._mlindent),
                    (self.lineno - 1, self._mllastlen - 1),
                    line
                )
                self._ml = False
                self._mlindent = 0
            elif end > 0:
                self._mltoken += line[self._mlindent:]
                self._mllastlen = len(line)
                return

        if line == '':
            yield self._eoftoken(line)
            return

        for m in ALLTOKENS_RE.finditer(line):
            token = m.group()
            start, end = m.span()

            if token == '\\':  # Escape
                if self.escape:
                    self.escape = False
                else:
                    self.escape = True
                    continue
            elif self.escape:
                self.escape = False
                if token != '\n':
                    yield self._token(NAME, token, start, end, line)

                continue

            if self.newline and (start == 0):  # Beginning of line
                lineindent = 0
                if token.startswith(' '):  # Whitespace
                    # Indentation
                    if self.coloffset < 0:
                        self.coloffset = end

                    elif not self.indentsize:
                        self.indentsize = end - self.coloffset

                    if self.indentsize and (end > self.coloffset):
                        lineindent = (end - self.coloffset) // self.indentsize

                elif token not in ['\n'] and self.coloffset < 0:
                    self.coloffset = start

                if lineindent > self.indent:
                    self.indent = lineindent
                    yield self._indenttoken(token, start, end, line)

                elif lineindent < self.indent:
                    for i in range(self.indent - lineindent):
                        self.indent -= 1
                        yield self._dedenttoken(lineindent, line)

            if token.startswith(' '):  # Whitespace
                # Ignore for the now.
                continue

            self.newline = token == '\n'
            if self.newline:
                yield self._newlinetoken(token, start, end, line)
                continue

            yield self._token(
                TOKENS_DICT.get(token, NAME),
                token,
                start,
                end,
                line
            )

            if token in (':', '#'):
                if line[end] == ' ':
                    end += 1
                if line[end] != '|':
                    yield from self._everything(start + 1, line)
                    self.newline = True
                    return

    def tokenizeline(self, line):
        for token in self._tokenizeline(line):
            if token.type == PIPE:
                self._mlmatch.append(token)
                continue
            elif token.type == NEWLINE and len(self._mlmatch) == 1:
                self._mlmatch.append(token)
                self._ml = True
                continue
            else:
                while self._mlmatch:
                    yield self._mlmatch.pop(0)
                yield token

    def tokenize(self, readline):
        eof = False

        while not eof:
            line = readline()
            for token in self.tokenizeline(line):
                yield token
                eof = token.type == EOF

    def tokenizes(self, string):
        # FIXME: Added due the bug:
        # https://github.com/brython-dev/brython/issues/1716
        if not string.endswith('\n'):
            string += '\n'

        yield from self.tokenize(io.StringIO(string).readline)


def tokenizes(string):
    yield from Tokenizer().tokenizes(string)
