"""
Pine Script Parser

Parses tokenized Pine Script code into an Abstract Syntax Tree (AST).
Supports Pine Script v1-v5 syntax.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Union

from .lexer import PineScriptLexer, Token, TokenType


# AST Node Types
@dataclass
class ASTNode:
    """Base class for all AST nodes"""

    line: int
    column: int


@dataclass
class Program(ASTNode):
    """Root node of the AST"""

    version: Optional[int] = None
    statements: List[ASTNode] = None

    def __post_init__(self):
        if self.statements is None:
            self.statements = []


@dataclass
class VersionDirective(ASTNode):
    """Version directive node (//@version=5)"""

    version: int


@dataclass
class FunctionDecl(ASTNode):
    """Function declaration"""

    name: str
    parameters: List[Parameter]
    return_type: Optional[str]
    body: List[ASTNode]
    is_export: bool = False


@dataclass
class Parameter(ASTNode):
    """Function parameter"""

    name: str
    type_qualifier: Optional[str] = None
    default_value: Optional[ASTNode] = None


@dataclass
class VariableDecl(ASTNode):
    """Variable declaration"""

    name: str
    value: Optional[ASTNode]
    is_var: bool = False  # var keyword
    is_varip: bool = False  # varip keyword
    type_annotation: Optional[str] = None


@dataclass
class Assignment(ASTNode):
    """Assignment statement"""

    target: str
    operator: str  # =, +=, -=, *=, /=
    value: ASTNode


@dataclass
class IfStatement(ASTNode):
    """If statement"""

    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None


@dataclass
class ForLoop(ASTNode):
    """For loop"""

    variable: str
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode]
    body: List[ASTNode]


@dataclass
class WhileLoop(ASTNode):
    """While loop"""

    condition: ASTNode
    body: List[ASTNode]


@dataclass
class FunctionCall(ASTNode):
    """Function call"""

    name: str
    arguments: List[Argument]


@dataclass
class Argument:
    """Function argument"""

    name: Optional[str]  # Named argument
    value: ASTNode


@dataclass
class BinaryOp(ASTNode):
    """Binary operation"""

    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    """Unary operation"""

    operator: str
    operand: ASTNode


@dataclass
class TernaryOp(ASTNode):
    """Ternary conditional (condition ? true_val : false_val)"""

    condition: ASTNode
    true_value: ASTNode
    false_value: ASTNode


@dataclass
class Literal(ASTNode):
    """Literal value (number, string, boolean)"""

    value: Any
    type: str  # 'number', 'string', 'bool', 'color'


@dataclass
class Identifier(ASTNode):
    """Identifier (variable or function reference)"""

    name: str


@dataclass
class ArrayAccess(ASTNode):
    """Array access (arr[index])"""

    array: ASTNode
    index: ASTNode


@dataclass
class MemberAccess(ASTNode):
    """Member access (obj.member)"""

    object: ASTNode
    member: str


class ParseError(Exception):
    """Parser error with line and column information"""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Parse error at {line}:{column}: {message}")
        self.line = line
        self.column = column


class PineScriptParser:
    """
    Recursive descent parser for Pine Script.

    Parses tokens into an Abstract Syntax Tree (AST).
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def error(self, message: str) -> ParseError:
        """Create a parse error at current position"""
        if self.current_token:
            return ParseError(
                message, self.current_token.line, self.current_token.column
            )
        return ParseError(message, 0, 0)

    def peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at tokens"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def advance(self) -> Token:
        """Move to next token"""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type"""
        if not self.current_token or self.current_token.type != token_type:
            raise self.error(
                f"Expected {token_type.name}, got {self.current_token.type.name if self.current_token else 'EOF'}"
            )
        return self.advance()

    def skip_newlines(self):
        """Skip newline tokens"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def parse(self) -> Program:
        """Parse the entire program"""
        program = Program(line=1, column=1)

        # Check for version directive
        if (
            self.current_token
            and self.current_token.type == TokenType.VERSION_DIRECTIVE
        ):
            version_str = self.current_token.value
            # Extract version number from //@version=5
            import re

            match = re.search(r"version\s*=\s*(\d+)", version_str)
            if match:
                program.version = int(match.group(1))
            self.advance()
            self.skip_newlines()

        # Parse statements
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            if self.current_token and self.current_token.type != TokenType.EOF:
                stmt = self.parse_statement()
                if stmt:
                    program.statements.append(stmt)
            self.skip_newlines()

        return program

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None

        token = self.current_token

        # Skip comments
        if token.type == TokenType.COMMENT:
            self.advance()
            return None

        # Variable declarations (var, varip)
        if token.type == TokenType.KEYWORD and token.value in ("var", "varip"):
            return self.parse_variable_decl()

        # If statement
        if token.type == TokenType.KEYWORD and token.value == "if":
            return self.parse_if_statement()

        # For loop
        if token.type == TokenType.KEYWORD and token.value == "for":
            return self.parse_for_loop()

        # While loop
        if token.type == TokenType.KEYWORD and token.value == "while":
            return self.parse_while_loop()

        # Try to parse as expression statement or assignment
        expr = self.parse_expression()

        # Check for assignment
        if self.current_token and self.current_token.type in (
            TokenType.ASSIGN,
            TokenType.PLUS_ASSIGN,
            TokenType.MINUS_ASSIGN,
            TokenType.MULTIPLY_ASSIGN,
            TokenType.DIVIDE_ASSIGN,
        ):
            if not isinstance(expr, Identifier):
                raise self.error("Invalid assignment target")

            operator = self.current_token.value
            line, col = self.current_token.line, self.current_token.column
            self.advance()

            value = self.parse_expression()

            return Assignment(
                target=expr.name,
                operator=operator,
                value=value,
                line=line,
                column=col,
            )

        return expr

    def parse_variable_decl(self) -> VariableDecl:
        """Parse variable declaration (var x = 10)"""
        token = self.current_token
        line, col = token.line, token.column

        is_var = token.value == "var"
        is_varip = token.value == "varip"
        self.advance()

        # Get variable name
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        # Optional type annotation
        type_annotation = None

        # Check for assignment
        value = None
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()

        return VariableDecl(
            name=name,
            value=value,
            is_var=is_var,
            is_varip=is_varip,
            type_annotation=type_annotation,
            line=line,
            column=col,
        )

    def parse_if_statement(self) -> IfStatement:
        """Parse if statement"""
        token = self.current_token
        line, col = token.line, token.column
        self.advance()  # Skip 'if'

        condition = self.parse_expression()

        self.skip_newlines()

        # Parse then branch
        then_branch = []
        # Single statement or block
        if self.current_token and self.current_token.type != TokenType.KEYWORD:
            stmt = self.parse_statement()
            if stmt:
                then_branch.append(stmt)

        self.skip_newlines()

        # Parse else branch
        else_branch = None
        if (
            self.current_token
            and self.current_token.type == TokenType.KEYWORD
            and self.current_token.value == "else"
        ):
            self.advance()  # Skip 'else'
            self.skip_newlines()
            else_branch = []
            stmt = self.parse_statement()
            if stmt:
                else_branch.append(stmt)

        return IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=line,
            column=col,
        )

    def parse_for_loop(self) -> ForLoop:
        """Parse for loop"""
        token = self.current_token
        line, col = token.line, token.column
        self.advance()  # Skip 'for'

        # Variable
        var_token = self.expect(TokenType.IDENTIFIER)
        variable = var_token.value

        self.expect(TokenType.ASSIGN)

        # Start value
        start = self.parse_expression()

        # 'to' keyword
        if not self.current_token or self.current_token.value != "to":
            raise self.error("Expected 'to' in for loop")
        self.advance()

        # End value
        end = self.parse_expression()

        # Optional step
        step = None
        if self.current_token and self.current_token.value == "by":
            self.advance()
            step = self.parse_expression()

        self.skip_newlines()

        # Body
        body = []
        stmt = self.parse_statement()
        if stmt:
            body.append(stmt)

        return ForLoop(
            variable=variable,
            start=start,
            end=end,
            step=step,
            body=body,
            line=line,
            column=col,
        )

    def parse_while_loop(self) -> WhileLoop:
        """Parse while loop"""
        token = self.current_token
        line, col = token.line, token.column
        self.advance()  # Skip 'while'

        condition = self.parse_expression()

        self.skip_newlines()

        # Body
        body = []
        stmt = self.parse_statement()
        if stmt:
            body.append(stmt)

        return WhileLoop(
            condition=condition,
            body=body,
            line=line,
            column=col,
        )

    def parse_expression(self) -> ASTNode:
        """Parse an expression"""
        return self.parse_ternary()

    def parse_ternary(self) -> ASTNode:
        """Parse ternary conditional (a ? b : c)"""
        expr = self.parse_logical_or()

        if self.current_token and self.current_token.type == TokenType.QUESTION:
            line, col = self.current_token.line, self.current_token.column
            self.advance()

            true_value = self.parse_expression()

            self.expect(TokenType.COLON)

            false_value = self.parse_expression()

            return TernaryOp(
                condition=expr,
                true_value=true_value,
                false_value=false_value,
                line=line,
                column=col,
            )

        return expr

    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR"""
        left = self.parse_logical_and()

        while (
            self.current_token
            and self.current_token.type == TokenType.KEYWORD
            and self.current_token.value == "or"
        ):
            op_token = self.current_token
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(
                left=left,
                operator="or",
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND"""
        left = self.parse_equality()

        while (
            self.current_token
            and self.current_token.type == TokenType.KEYWORD
            and self.current_token.value == "and"
        ):
            op_token = self.current_token
            self.advance()
            right = self.parse_equality()
            left = BinaryOp(
                left=left,
                operator="and",
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    def parse_equality(self) -> ASTNode:
        """Parse equality operators (==, !=)"""
        left = self.parse_comparison()

        while self.current_token and self.current_token.type in (
            TokenType.EQUALS,
            TokenType.NOT_EQUALS,
        ):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(
                left=left,
                operator=operator,
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    def parse_comparison(self) -> ASTNode:
        """Parse comparison operators (<, >, <=, >=)"""
        left = self.parse_addition()

        while self.current_token and self.current_token.type in (
            TokenType.LESS_THAN,
            TokenType.GREATER_THAN,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        ):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_addition()
            left = BinaryOp(
                left=left,
                operator=operator,
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    def parse_addition(self) -> ASTNode:
        """Parse addition and subtraction"""
        left = self.parse_multiplication()

        while self.current_token and self.current_token.type in (
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(
                left=left,
                operator=operator,
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication, division, modulo"""
        left = self.parse_unary()

        while self.current_token and self.current_token.type in (
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.MODULO,
        ):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(
                left=left,
                operator=operator,
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    def parse_unary(self) -> ASTNode:
        """Parse unary operators (-, not)"""
        if self.current_token and (
            self.current_token.type == TokenType.MINUS
            or (
                self.current_token.type == TokenType.KEYWORD
                and self.current_token.value == "not"
            )
        ):
            op_token = self.current_token
            operator = op_token.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(
                operator=operator,
                operand=operand,
                line=op_token.line,
                column=op_token.column,
            )

        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        """Parse postfix operations (function calls, array access, member access)"""
        expr = self.parse_primary()

        while True:
            if not self.current_token:
                break

            # Function call
            if self.current_token.type == TokenType.LPAREN:
                line, col = self.current_token.line, self.current_token.column
                self.advance()

                arguments = self.parse_arguments()

                self.expect(TokenType.RPAREN)

                if isinstance(expr, Identifier):
                    expr = FunctionCall(
                        name=expr.name,
                        arguments=arguments,
                        line=line,
                        column=col,
                    )
                else:
                    raise self.error("Invalid function call")

            # Array access
            elif self.current_token.type == TokenType.LBRACKET:
                line, col = self.current_token.line, self.current_token.column
                self.advance()

                index = self.parse_expression()

                self.expect(TokenType.RBRACKET)

                expr = ArrayAccess(
                    array=expr,
                    index=index,
                    line=line,
                    column=col,
                )

            # Member access
            elif self.current_token.type == TokenType.DOT:
                line, col = self.current_token.line, self.current_token.column
                self.advance()

                member_token = self.expect(TokenType.IDENTIFIER)

                expr = MemberAccess(
                    object=expr,
                    member=member_token.value,
                    line=line,
                    column=col,
                )

            else:
                break

        return expr

    def parse_arguments(self) -> List[Argument]:
        """Parse function arguments"""
        arguments = []

        while self.current_token and self.current_token.type != TokenType.RPAREN:
            # Check for named argument
            name = None
            if (
                self.current_token.type == TokenType.IDENTIFIER
                and self.peek(1)
                and self.peek(1).type == TokenType.ASSIGN
            ):
                name = self.current_token.value
                self.advance()  # Skip name
                self.advance()  # Skip =

            value = self.parse_expression()

            arguments.append(Argument(name=name, value=value))

            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            else:
                break

        return arguments

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions (literals, identifiers, parenthesized expressions)"""
        if not self.current_token:
            raise self.error("Unexpected end of input")

        token = self.current_token

        # Numbers
        if token.type == TokenType.NUMBER:
            self.advance()
            return Literal(
                value=float(token.value) if "." in token.value else int(token.value),
                type="number",
                line=token.line,
                column=token.column,
            )

        # Strings
        if token.type == TokenType.STRING:
            self.advance()
            return Literal(
                value=token.value,
                type="string",
                line=token.line,
                column=token.column,
            )

        # Booleans
        if token.type == TokenType.BOOL:
            self.advance()
            return Literal(
                value=token.value == "true",
                type="bool",
                line=token.line,
                column=token.column,
            )

        # Identifiers
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(
                name=token.value,
                line=token.line,
                column=token.column,
            )

        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise self.error(f"Unexpected token: {token.type.name}")


def parse_pine_script(code: str) -> Program:
    """
    Parse Pine Script code into an AST.

    Args:
        code: Pine Script source code

    Returns:
        Program AST node

    Raises:
        ParseError: If parsing fails
    """
    lexer = PineScriptLexer(code)
    tokens = lexer.tokenize()
    parser = PineScriptParser(tokens)
    return parser.parse()
