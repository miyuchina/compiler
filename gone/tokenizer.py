# gone/tokenizer.py
r'''
Project 1 - Write a Lexer
=========================
In the first project, you are going to write a simple lexer for a
subset of the Gone language.  The project is presented as code that
you must read and extend (this file).  Please read the complete
contents of this file and carefully complete the steps indicated by
comments.

Overview:
---------
The process of lexing is that of taking input text and breaking it
down into a stream of tokens. Each token is like a valid word from the
dictionary.  Essentially, the role of the lexer is to simply make sure
that the input text consists of valid symbols and tokens prior to any
further processing related to parsing.

Each token is defined by a regular expression.  Thus, your primary task
in this first project is to define a set of regular expressions for
the language.  The actual job of lexing will be handled by SLY
(https://github.com/dabeaz/sly)

Specification:
--------------
Your lexer must recognize the following symbols and tokens.  The name
on the left is the token name, the value on the right is the matching
text.  Note: Additional features will be added in later projects.

Reserved Keywords:
    CONST   : 'const'
    VAR     : 'var'  
    PRINT   : 'print'

Identifiers (Same rules as for Python):
    ID      : Text starting with a letter or '_', followed by any number
              number of letters, digits, or underscores.
              Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

Operators and Delimiters:
    PLUS     : '+'
    MINUS    : '-'
    TIMES    : '*'
    DIVIDE   : '/'
    ASSIGN   : '='
    SEMI     : ';'
    LPAREN   : '('
    RPAREN   : ')'

Literals:
    INTEGER :  123   (decimal)

    FLOAT   : 1.234
              .1234
              1234.

    CHAR    : 'a'     (a single character - byte)
              '\''    The quote
              '\n'    Newline
              '\\'    Backslash
              '\xhh'  (byte value)


Comments:  To be ignored by your lexer
     //             Skips the rest of the line
     /* ... */      Skips a block (no nesting allowed)

Errors: Your lexer must recognized and report the following error messages:

     lineno: Illegal char 'c'         
     lineno: Unterminated character constant     
     lineno: Unterminated comment

Testing
-------
To get started, look at Tests/lextest[0-5].g.  Work through each file
in sequence.  Run your tokenize like this:

     bash % python3 -m gone.tokenizer lextest0.g
     bash % python3 -m gone.tokenizer lextest1.g

Bonus: Think about how to write proper unit tests.
'''

# ----------------------------------------------------------------------
# The following import loads a function error(lineno, msg) that should be
# used to report all error messages issued by your lexer.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# -----------------------------------------------------------------------
# The SLY package. https://github.com/dabeaz/sly
from sly import Lexer

# -----------------------------------------------------------------------
# Lexers are defined by a class that inherits from sly.Lexer.  Follow
# the instructions contained in the class below.

class GoneLexer(Lexer):
    # ----------------------------------------------------------------------
    # Token set. This set identifies the complete list of token names
    # to be recognized by your lexer.  A few tokens have been given, you'll
    # need to add more (see description above)

    tokens = {
        # keywords
        'PRINT', 'CONST', 'VAR', 'IF', 'ELSE', 'WHILE', 'FUNC', 'RETURN', 'FOR',
        'BREAK', 'CONTINUE',
                 
        # Identifiers
        'ID',

        # Literals
        'INTEGER', 'FLOAT', 'CHAR',
        'TRUE', 'FALSE',

        # Operators 
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN',
        'LT', 'GT', 'LE', 'GE', 'EQ', 'NE', 'AND', 'OR', 'NOT',
        'AUG_PLUS', 'AUG_MINUS', 'AUG_TIMES', 'AUG_DIVIDE',
        'INCR', 'DECR',

        # Other symbols
        'LPAREN', 'RPAREN', 'LCBRACE', 'RCBRACE', 'SEMI', 'COMMA',
    }

    # ----------------------------------------------------------------------
    # Ignored characters (whitespace)
    #
    # The following individual characters are ignored completely by the lexer
    # when they appear between tokens.  Do not change.
    ignore = ' \t\r'

    # ----------------------------------------------------------------------
    # Ignored patterns.  You'll need to supply appropriate regexes.
    # For example:
    #    
    #    ignore_COMMENT = r'regex for a block-style-comment'
    #
    # or
    #
    #    @_(r'regex for a block-style comment')
    #    def COMMENT(self, t):
    #        ... some processing ...
    #        return None
    #

    # block-style comment (/* ... */)

    # line-style comment (//...)

    # One or more newlines \n\n\n...

    @_(r'//.*?\n')
    def ignore_line_comment(self, token):
        self.lineno += 1

    @_(r'/\*[\s\S]*?\*/')
    def ignore_block_comment(self, token):
        self.lineno += token.value.count('\n')

    @_(r'/\*[\s\S]*')
    def ignore_unterminated_comment(self, token):
        error(self.lineno, f"Unterminated comment {repr(token.value)}")
        self.lineno += 1


    @_(r'\n+')
    def ignore_newlines(self, token):
        self.lineno += token.value.count('\n')


    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : write the regexs indicated below ***
    # 
    # Tokens for simple symbols: + - * / = ( ) ; 
    #
    # Caution: Definition order matters. Longer symbols should appear 
    # before shorter symbols that are a substring (for example, the
    # pattern for <= should go before <).

    LE     = r'<='
    GE     = r'>='
    LT     = r'<'
    GT     = r'>'
    EQ     = r'=='
    NE     = r'!='
    AND    = r'&&'
    OR     = r'\|\|'
    NOT    = r'\!'

    INCR = '\+\+'
    DECR = '--'

    AUG_PLUS   = r'\+='
    AUG_MINUS  = r'-='
    AUG_TIMES  = r'\*='
    AUG_DIVIDE = r'/='

    PLUS    = r'\+'      # Regex for a single plus sign
    MINUS   = r'-'       # Regex for a single minus sign
    TIMES   = r'\*'
    DIVIDE  = r'/'
    ASSIGN  = r'='
    LPAREN  = r'\('
    RPAREN  = r'\)'
    LCBRACE = r'\{'
    RCBRACE = r'\}'
    SEMI    = r';'
    COMMA   = ','

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : write the regexs and additional code below ***
    #
    # Tokens for literals, INTEGER, FLOAT, STRING. 

    # Floating point constant.   You must recognize floating point numbers in
    # the following formats:
    #
    #   1.23
    #   123.
    #   .123
    #
    # Bonus: Recognize floating point numbers in scientific notation 
    #
    #   1.23e1
    #   1.23e+1
    #   1.23e-1
    #   1e1

    FLOAT = r'(\d+\.?\d*[Ee][+-]?\d+)|(\d+\.\d*)|(\d*\.\d+)'

    # ----- YOU IMPLEMENT

    # Integer literal
    #
    #     1234             (decimal)
    #
    # Bonus: Recognize integers in different bases such as 0x1a, 0o13 or 0b111011.

    INTEGER = r'\b(\d+|(0[a-z][\da-z]+))\b'

    # ----- YOU IMPLEMENT

    # Character constant. You must recognize a single letter enclosed in single quotes
    # For example:
    #
    #     'a'
    #
    # Escape codes should also be be recognized:
    #
    #     '\n'    - Newline
    #     '\\'    - Backslash
    #     '\''    - Quote
    #     '\xhh'  - Generic byte

    # ----- YOU IMPLEMENT

    @_(r"'\\[n\\']'|'\\x[0-9a-f]{2}'|'.'")
    def CHAR(self, token):
        return token

    @_(r"\'.")
    def unterminated_char(self, token):
        error(self.lineno, f"Unterminated character {repr(token.value)}")

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : Write the regex and add keywords ***
    #
    # Identifiers and keywords. 
    #
    # Match a raw identifier.  Identifiers follow the same rules as Python.
    # That is, they start with a letter or underscore (_) and can contain
    # an arbitrary number of letters, digits, or underscores after that.
    # Language keywords such as "if" and "while" are also matched as 
    # identifiers. You need to catch these and change their token type
    # to match the appropriate keyword.

    # ----- YOU IMPLEMENT

    @_(r'\b[a-zA-Z_][a-zA-Z_0-9]*\b')
    def ID(self, token):
        keywords = {'const', 'var', 'print', 'true', 'false',
                    'if', 'else', 'while', 'func', 'return', 'for',
                    'break', 'continue'}
        if token.value in keywords:
            token.type = token.value.upper()
        return token

    # ----------------------------------------------------------------------
    # Bad character error handling
    def error(self, t):
        error(self.lineno,"Illegal character %r" % t.value[0])
        self.index += 1
    
# ----------------------------------------------------------------------
#                DO NOT CHANGE ANYTHING BELOW THIS PART
#
# Use this main program to test/debug your lexer.  Run it using the -m option
#
#    bash % python3 -m gone.tokenizer filename.g
#
# ----------------------------------------------------------------------
def main():
    '''
    Main program. For debugging purposes.
    '''
    import sys
    
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.tokenizer filename\n")
        raise SystemExit(1)

    lexer = GoneLexer()
    text = open(sys.argv[1]).read()
    for tok in lexer.tokenize(text):
        print(tok)

if __name__ == '__main__':
    main()

