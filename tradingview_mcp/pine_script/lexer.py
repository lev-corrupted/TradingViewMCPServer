"""
Pine Script Lexer and Tokenizer

Tokenizes Pine Script code into a stream of tokens for parsing.
Supports Pine Script v1-v5 syntax.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Iterator


class TokenType(Enum):
    """Token types for Pine Script"""

    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    COLOR = auto()

    # Identifiers and Keywords
    IDENTIFIER = auto()
    KEYWORD = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    QUESTION = auto()
    COLON = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    ARROW = auto()

    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    COMMENT = auto()
    VERSION_DIRECTIVE = auto()
    EOF = auto()

    # Assignment operators
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()


@dataclass
class Token:
    """Represents a single token in Pine Script code"""
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# Pine Script keywords across all versions
KEYWORDS = {
    # v1-v6 common keywords
    'if', 'else', 'for', 'while', 'break', 'continue',
    'true', 'false', 'na', 'and', 'or', 'not',

    # Type declarations (v4+)
    'var', 'varip',

    # Function/method keywords
    'method', 'export',

    # Import/library (v5+)
    'import', 'as',

    # Type keywords (v5+)
    'type',

    # Control flow
    'switch', 'return',

    # v6 keywords
    'struct', 'enum',
}

# Built-in functions and types
BUILTIN_FUNCTIONS = {
    'plot', 'plotshape', 'plotchar', 'plotarrow', 'plotbar', 'plotcandle',
    'hline', 'fill', 'bgcolor',
    'strategy', 'study', 'indicator', 'library',
    'security', 'request.security',
    'close', 'open', 'high', 'low', 'volume', 'time', 'bar_index',
    'ta.sma', 'ta.ema', 'ta.rsi', 'ta.macd', 'ta.stoch',
    'math.abs', 'math.max', 'math.min', 'math.round', 'math.floor', 'math.ceil',
    'str.tostring', 'str.tonumber', 'str.length',
    'array.new', 'array.size', 'array.push', 'array.pop', 'array.get', 'array.set',
    'input', 'input.int', 'input.float', 'input.string', 'input.bool',
}

# Type qualifiers
TYPE_QUALIFIERS = {
    'series', 'simple', 'const', 'input',
    'int', 'float', 'bool', 'color', 'string',
    'line', 'label', 'box', 'table', 'array', 'matrix',
}


class PineScriptLexer:
    """
    Lexical analyzer for Pine Script code.

    Converts source code into a stream of tokens.
    """

    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, message: str) -> Exception:
        """Create a lexer error with position information"""
        return SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")

    def peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead in the source code"""
        pos = self.pos + offset
        if pos < len(self.code):
            return self.code[pos]
        return None

    def advance(self) -> Optional[str]:
        """Move to the next character"""
        if self.pos >= len(self.code):
            return None

        char = self.code[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self):
        """Skip whitespace except newlines"""
        while self.peek() and self.peek() in ' \t\r':
            self.advance()

    def read_number(self) -> Token:
        """Read a numeric literal"""
        start_line = self.line
        start_col = self.column
        num_str = ''

        # Handle negative numbers
        if self.peek() == '-':
            num_str += self.advance()

        # Read digits and decimal point
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            num_str += self.advance()

        # Handle scientific notation
        if self.peek() and self.peek() in 'eE':
            num_str += self.advance()
            if self.peek() and self.peek() in '+-':
                num_str += self.advance()
            while self.peek() and self.peek().isdigit():
                num_str += self.advance()

        return Token(TokenType.NUMBER, num_str, start_line, start_col)

    def read_string(self, quote: str) -> Token:
        """Read a string literal"""
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote

        string_val = ''
        while True:
            char = self.peek()

            if char is None:
                raise self.error("Unterminated string")

            if char == quote:
                self.advance()  # Skip closing quote
                break

            if char == '\\':
                self.advance()
                next_char = self.advance()
                if next_char in 'nrt\\"\'\n':
                    string_val += '\\' + (next_char or '')
                else:
                    string_val += next_char or ''
            else:
                string_val += self.advance()

        return Token(TokenType.STRING, string_val, start_line, start_col)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword"""
        start_line = self.line
        start_col = self.column
        ident = ''

        # Read identifier characters (alphanumeric + underscore + dot for namespaces)
        while self.peek() and (self.peek().isalnum() or self.peek() in '_.'):
            ident += self.advance()

        # Check for boolean literals first
        if ident in ('true', 'false'):
            token_type = TokenType.BOOL
        # Check for na (special value, treat as identifier not keyword)
        elif ident == 'na':
            token_type = TokenType.IDENTIFIER
        # Check if it's a keyword
        elif ident in KEYWORDS:
            token_type = TokenType.KEYWORD
        else:
            token_type = TokenType.IDENTIFIER

        return Token(token_type, ident, start_line, start_col)

    def read_comment(self) -> Token:
        """Read a comment"""
        start_line = self.line
        start_col = self.column
        comment = ''

        # Single-line comment
        if self.peek() == '/' and self.peek(1) == '/':
            self.advance()  # First /
            self.advance()  # Second /

            while self.peek() and self.peek() != '\n':
                comment += self.advance()

            return Token(TokenType.COMMENT, comment.strip(), start_line, start_col)

        return None

    def read_version_directive(self) -> Optional[Token]:
        """Read Pine Script version directive (e.g., //@version=5)"""
        if self.peek() == '/' and self.peek(1) == '/' and self.peek(2) == '@':
            start_line = self.line
            start_col = self.column
            directive = ''

            while self.peek() and self.peek() != '\n':
                directive += self.advance()

            return Token(TokenType.VERSION_DIRECTIVE, directive.strip(), start_line, start_col)

        return None

    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        self.tokens = []

        while self.pos < len(self.code):
            self.skip_whitespace()

            char = self.peek()

            if char is None:
                break

            # Newlines
            if char == '\n':
                token = Token(TokenType.NEWLINE, '\\n', self.line, self.column)
                self.tokens.append(token)
                self.advance()
                continue

            # Version directive or comment
            if char == '/':
                version_token = self.read_version_directive()
                if version_token:
                    self.tokens.append(version_token)
                    continue

                comment_token = self.read_comment()
                if comment_token:
                    self.tokens.append(comment_token)
                    continue

            # Numbers
            if char.isdigit() or (char == '-' and self.peek(1) and self.peek(1).isdigit()):
                self.tokens.append(self.read_number())
                continue

            # Strings
            if char in '"\'':
                self.tokens.append(self.read_string(char))
                continue

            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue

            # Operators and delimiters
            start_line = self.line
            start_col = self.column

            # Two-character operators
            two_char = char + (self.peek(1) or '')

            if two_char == '==':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQUALS, '==', start_line, start_col))
            elif two_char == '!=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUALS, '!=', start_line, start_col))
            elif two_char == '<=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_line, start_col))
            elif two_char == '>=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_line, start_col))
            elif two_char == '=>':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '=>', start_line, start_col))
            elif two_char == '+=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_col))
            elif two_char == '-=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_col))
            elif two_char == '*=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY_ASSIGN, '*=', start_line, start_col))
            elif two_char == '/=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE_ASSIGN, '/=', start_line, start_col))
            # Single-character operators
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_col))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_col))
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_col))
            elif char == '=':
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            elif char == '<':
                self.advance()
                self.tokens.append(Token(TokenType.LESS_THAN, '<', start_line, start_col))
            elif char == '>':
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_THAN, '>', start_line, start_col))
            elif char == '?':
                self.advance()
                self.tokens.append(Token(TokenType.QUESTION, '?', start_line, start_col))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_col))
            else:
                raise self.error(f"Unexpected character: {char!r}")

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))

        return self.tokens
