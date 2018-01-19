# gone/parser.py
'''
Project 2:  Write a parser
==========================
In this project, you write the basic shell of a parser for Gone.  A
formal BNF of the language follows.  Your task is to write parsing
rules and build the AST for this grammar using SLY.  The following
grammar is partial.  More features get added in later projects.

program : statements
        | empty

statements :  statements statement
           |  statement

statement :  const_declaration
          |  var_declaration
          |  assign_statement
          |  print_statement
    
const_declaration : CONST ID = expression ;

var_declaration : VAR ID datatype ;
                | VAR ID datatype = expression ;

assign_statement : location = expression ;

print_statement : PRINT expression ;

expression :  + expression
           |  - expression
           | expression + expression
           | expression - expression
           | expression * expression
           | expression / expression
           | ( expression )
           | location
           | literal

literal : INTEGER     
        | FLOAT       
        | CHAR      

location : ID
         ;

datatype : ID
         ;

empty    :

To do the project, follow the instructions contained below.
'''

# ----------------------------------------------------------------------
# parsers are defined using SLY.  You inherit from the Parser class
#
# See http://sly.readthedocs.io/en/latest/
# ----------------------------------------------------------------------
from sly import Parser

# ----------------------------------------------------------------------
# The following import loads a function error(lineno,msg) that should be
# used to report all error messages issued by your parser.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# ----------------------------------------------------------------------
# Import the lexer class.  It's token list is needed to validate and
# build the parser object.
from .tokenizer import GoneLexer

# ----------------------------------------------------------------------
# Get the AST nodes.  
# Read instructions in ast.py
from .ast import *

class GoneParser(Parser):
    # Same token set as defined in the lexer
    tokens = GoneLexer.tokens

    # ----------------------------------------------------------------------
    # Operator precedence table.   Operators must follow the same 
    # precedence rules as in Python.  Instructions to be given in the project.

    precedence = (
            ('left', 'OR'),
            ('left', 'AND'),
            ('nonassoc', 'LE', 'GE', 'LT', 'GT', 'EQ', 'NE'),
            ('left', 'PLUS', 'MINUS'),
            ('left', 'TIMES', 'DIVIDE'),
            ('right', 'NOT'),
    )

    # ----------------------------------------------------------------------
    # YOUR TASK.   Translate the BNF in the string below into a collection
    # of parser functions.  For example, a rule such as :
    #
    #   program : statements
    #
    # Gets turned into a Python method like this:
    #
    # @_('statements')
    # def program(self, p):
    #      return Program(p.statements)
    #
    # For symbols such as '(' or '+', you'll need to replace with the name
    # of the corresponding token such as LPAREN or PLUS.
    #
    # In the body of each rule, create an appropriate AST node and return it
    # as shown above.
    #
    # For the purposes of lineno number tracking, you should assign a line number
    # to each AST node as appropriate.  To do this, I suggest pulling the 
    # line number off of any nearby terminal symbol.  For example:
    #
    # @_('PRINT expr SEMI')
    # def print_statement(self, p):
    #     return PrintStatement(p.expr, lineno=p.lineno)
    #
    # STARTING OUT
    # ============
    # The following grammar rules should give you an idea of how to start.
    # Try running this file on the input Tests/parsetest0.g
    #
    # Afterwards, add features by looking at the code in Tests/parsetest1-6.g

    @_('statements', 'empty')
    def block(self, p):
        return p[0]

    @_('statements statement')
    def statements(self, p):
        p.statements.append(p.statement)
        return p.statements

    @_('statement')
    def statements(self, p):
        return [p.statement]

    @_('assignment_statement SEMI',
       'const_statement SEMI',
       'var_statement SEMI',
       'if_statement',
       'while_statement',
       'for_statement',
       'func_statement',
       'break_statement',
       'continue_statement',
       'return_statement',
       'print_statement SEMI')
    def statement(self, p):
        return p[0]

    @_('location AUG_PLUS expression',
       'location AUG_MINUS expression',
       'location AUG_TIMES expression',
       'location AUG_DIVIDE expression')
    def assignment_statement(self, p):
        expr = BinOp(p[1][0], ReadLocation(p.location, lineno=p.lineno), p.expression)
        return Assignment(p.location, expr, lineno=p.lineno)

    @_('location INCR',
       'location DECR',)
    def assignment_statement(self, p):
        expr = BinOp(p[1][0], ReadLocation(p.location, lineno=p.lineno), IntegerLiteral(1, lineno=p.lineno))
        return Assignment(p.location, expr, lineno=p.lineno)


    @_('location ASSIGN expression')
    def assignment_statement(self, p):
        return Assignment(p.location, p.expression, lineno=p.lineno)

    @_('CONST location ASSIGN expression')
    def const_statement(self, p):
        return ConstDeclaration(p.location, p.expression, lineno=p.lineno)

    @_('VAR location datatype ASSIGN expression')
    def var_statement(self, p):
        return VarDeclaration(p.location, p.datatype, p.expression, lineno=p.lineno)

    @_('VAR location datatype')
    def var_statement(self, p):
        return VarDeclaration(p.location, p.datatype, None, lineno=p.lineno)

    @_('PRINT expression')
    def print_statement(self, p):
        return PrintStatement(p.expression, lineno=p.lineno)

    @_('ID')
    def datatype(self, p):
        return SimpleType(p.ID, lineno=p.lineno)

    @_('expression PLUS expression',
       'expression MINUS expression',
       'expression TIMES expression',
       'expression DIVIDE expression')
    def expression(self, p):
        return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('PLUS expression',
       'MINUS expression')
    def expression(self, p):
        return UnaryOp(p[0], p.expression, lineno=p.lineno)

    @_('LPAREN expression RPAREN')
    def expression(self, p):
        return p.expression

    @_('expression LE expression',
       'expression GE expression',
       'expression LT expression',
       'expression GT expression',
       'expression EQ expression',
       'expression NE expression',
       'expression AND expression',
       'expression OR expression')
    def expression(self, p):
        return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('NOT expression')
    def expression(self, p):
        return UnaryOp(p.NOT, p.expression, lineno=p.lineno)

    @_('function_call')
    def expression(self, p):
        return p.function_call

    @_('location')
    def expression(self, p):
        return ReadLocation(p.location, lineno=p.location.lineno)

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('IF expression LCBRACE block RCBRACE ELSE LCBRACE block RCBRACE')
    def if_statement(self, p):
        return IfStatement(p.expression, p.block0, p.block1, lineno=p.lineno)

    @_('IF expression LCBRACE block RCBRACE')
    def if_statement(self, p):
        return IfStatement(p.expression, p.block, [], lineno=p.lineno)

    @_('WHILE expression LCBRACE block RCBRACE')
    def while_statement(self, p):
        return WhileStatement(p.expression, p.block, lineno=p.lineno)

    @_('FOR LPAREN statement expression SEMI statement RPAREN LCBRACE block RCBRACE')
    def for_statement(self, p):
        return ForStatement(p.statement0, p.expression, p.statement1, p.block, lineno=p.lineno)

    @_('FOR statement expression SEMI statement LCBRACE block RCBRACE')
    def for_statement(self, p):
        return ForStatement(p.statement0, p.expression, p.statement1, p.block, lineno=p.lineno)

    # functions ===============================================================
    @_('FUNC ID LPAREN arguments RPAREN datatype LCBRACE block RCBRACE')
    def func_statement(self, p):
        return FuncDeclaration(p.ID, p.arguments, p.datatype, p.block, lineno=p.lineno)

    @_('BREAK SEMI')
    def break_statement(self, p):
        return BreakStatement(p.BREAK, lineno=p.lineno)

    @_('CONTINUE SEMI')
    def continue_statement(self, p):
        return ContinueStatement(p.CONTINUE, lineno=p.lineno)

    @_('RETURN expression SEMI')
    def return_statement(self, p):
        return ReturnStatement(p.expression, lineno=p.lineno)

    @_('RETURN SEMI')
    def return_statement(self, p):
        return ReturnStatement(None, lineno=p.lineno)

    @_('arguments COMMA argument')
    def arguments(self, p):
        p.arguments.append(p.argument)
        return p.arguments

    @_('argument')
    def arguments(self, p):
        return [p.argument]

    @_('empty')
    def arguments(self, p):
        return []

    @_('ID datatype')
    def argument(self, p):
        return FuncArgument(p.ID, p.datatype, lineno=p.lineno)

    @_('location LPAREN call_arguments RPAREN')
    def function_call(self, p):
        return FunctionCall(p.location, p.call_arguments, lineno=p.lineno)

    @_('call_arguments COMMA expression')
    def call_arguments(self, p):
        p.call_arguments.append(p.expression)
        return p.call_arguments

    @_('expression')
    def call_arguments(self, p):
        return [p.expression]

    @_('empty')
    def call_arguments(self, p):
        return []
    # =========================================================================

    @_('ID')
    def location(self, p):
        return SimpleLocation(p.ID, lineno=p.lineno)

    @_('INTEGER')
    def literal(self, p):
        return IntegerLiteral(int(p.INTEGER), lineno=p.lineno)

    @_('FLOAT')
    def literal(self, p):
        return FloatLiteral(float(p.FLOAT), lineno=p.lineno)

    @_('CHAR')
    def literal(self, p):
        return CharLiteral(eval(p.CHAR), lineno=p.lineno)

    @_('TRUE', 'FALSE')
    def literal(self, p):
        return BoolLiteral(eval(p[0].title()), lineno=p.lineno)

    @_('')
    def empty(self, p):
        return []

    # ----------------------------------------------------------------------
    # DO NOT MODIFY
    #
    # catch-all error handling.   The following function gets called on any
    # bad input.  p is the offending token or None if end-of-file (EOF).
    def error(self, p):
        if p:
            error(p.lineno, "Syntax error in input at token '%s'" % p.value)
        else:
            error('EOF','Syntax error. No more input.')

# ----------------------------------------------------------------------
#                     DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

def parse(source):
    '''
    Parse source code into an AST. Return the top of the AST tree.
    '''
    lexer = GoneLexer()
    parser = GoneParser()
    ast = parser.parse(lexer.tokenize(source))
    return ast

def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.parser filename\n')
        raise SystemExit(1)

    # Parse and create the AST
    ast = parse(open(sys.argv[1]).read())

    # Output the resulting parse tree structure
    for depth, node in flatten(ast):
        print('%s: %s%s' % (getattr(node, 'lineno', None), ' '*(4*depth), node))

if __name__ == '__main__':
    main()
