from unittest import TestCase
from unittest.mock import patch
from gone.tokenizer import GoneLexer

class TestTokenizer(TestCase):
    def setUp(self):
        self.lexer = GoneLexer()
        self.patcher = patch('builtins.print', mock_print)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    # lextest0 ================================================================
    def test_simple_tokens(self):
        text = "+ - * / = ; ( )"
        token_types = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'SEMI',
                       'LPAREN', 'RPAREN']
        for token, token_type in zip(self.lexer.tokenize(text), token_types):
            self.assertEqual(token.type, token_type)

    # lextest1 ================================================================
    def test_keywords(self):
        text = "const var print"
        token_types = text.upper().split()
        for token, token_type in zip(self.lexer.tokenize(text), token_types):
            self.assertEqual(token.type, token_type)

    def test_identifiers(self):
        text = "a z  A Z _a _z _A _Z a123 A123 a123z A123Z"
        tokens = [('ID', identifier) for identifier in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    def test_tricky_identifiers(self):
        text = "printer variable constant"
        tokens = [('ID', identifier) for identifier in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    # lextest2 ================================================================
    def test_integers(self):
        text = "1234"
        tokens = [('INTEGER', '1234')]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    def test_bonus_integers(self):
        text = "0x1234 0b1101011 0o123"
        tokens = [('INTEGER', number) for number in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    def test_floats(self):
        text = "1.23 123. .123 0. .0"
        tokens = [('FLOAT', number) for number in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    def test_bonus_floats(self):
        text = "1.23e1 1.23e+1 1.23e-1 123e1 1.23E1 1.23E+1"
        tokens = [('FLOAT', number) for number in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    # lextest3 ================================================================
    def test_character_literals(self):
        text = r"'a' '\n' '\x3f' '\'' '\\'"
        tokens = [('CHAR', char) for char in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    # lextest5 ================================================================
    def test_illegal_characters(self):
        text = 'a$ 123@ b\n\'H\n/* Unterminated C-style comment'
        with self.assertRaises(AssertionError) as ctx:
            for token in self.lexer.tokenize(text):
                token

    # project6
    def test_boolean_operators(self):
        text = "< > <= >= == != && || !"
        tokens = ['LT', 'GT', 'LE', 'GE', 'EQ', 'NE', 'AND', 'OR', 'NOT']
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    def test_boolean_literals(self):
        text = "true false"
        tokens = text.upper().split()
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    def test_not_boolean_keywords(self):
        text = "true_value falsehood"
        tokens = [('ID', value) for value in text.split()]
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected[0])
            self.assertEqual(token.value, expected[1])

    # project7
    def test_control_flow_keywords(self):
        text = "if else while"
        tokens = text.upper().split()
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    def test_curly_braces(self):
        text = "{ }"
        tokens = ['LCBRACE', 'RCBRACE']
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    # project8
    def test_func_and_return(self):
        text = 'func return'
        tokens = text.upper().split()
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    def test_comma(self):
        text = ','
        tokens = ['COMMA']
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    # for loop
    def test_for_loop(self):
        text = 'for'
        tokens = ['FOR']
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

    # break; continue
    def test_break_continue(self):
        text = 'break continue'
        tokens = text.upper().split()
        for token, expected in zip(self.lexer.tokenize(text), tokens):
            self.assertEqual(token.type, expected)

def mock_print(*args, **kwargs):
    import sys
    if len(kwargs) == 0:
        sys.stderr.write(str(*args))
    raise AssertionError(args)

