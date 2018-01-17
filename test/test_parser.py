from unittest import TestCase
from unittest.mock import patch
from gone.tokenizer import GoneLexer
from gone.parser import GoneParser
from gone.ast import *

class TestParser(TestCase):
    def setUp(self):
        self.patcher = patch('builtins.print', mock_print)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def parse(self, source):
        lexer = GoneLexer()
        parser = GoneParser()
        return parser.parse(lexer.tokenize(source))

    # parsetest0 ==============================================================
    def test_print_statement(self):
        ast = self.parse("print 42;")
        self.assertIsInstance(ast[0], PrintStatement)
        self.assertIsInstance(ast[0].value, IntegerLiteral)
        self.assertEqual(ast[0].value.value, 42)

    # parsetest1 ==============================================================
    def test_multiple_statements(self):
        text = ("print 42;\n"
                "print 3.14159;\n"
                "print 'a';\n")
        ast = self.parse(text)
        tokens = [(PrintStatement, value) for value in (42, 3.14159, 'a')]
        for token, expected in zip(ast, tokens):
            self.assertIsInstance(token, expected[0])
            self.assertEqual(token.value.value, expected[1])

    # parsetest2 ==============================================================
    def test_binary_operations(self):
        text = ("print 1 + 2;\n"
                "print 1 - 2;\n"
                "print 1 * 2;\n"
                "print 1 / 2;\n")
        ast = self.parse(text)
        tokens = [(PrintStatement, BinOp)] * 4
        for token, expected in zip(ast, tokens):
            self.assertIsInstance(token, expected[0])
            self.assertIsInstance(token.value, expected[1])
            self.assertIsInstance(token.value.left, IntegerLiteral)
            self.assertEqual(token.value.left.value, 1)
            self.assertIsInstance(token.value.right, IntegerLiteral)
            self.assertEqual(token.value.right.value, 2)

    def test_unary_operations(self):
        text = ("print -1;\n"
                "print +1;\n")
        ast = self.parse(text)
        tokens = [(PrintStatement, UnaryOp)] * 2
        for token, expected in zip(ast, tokens):
            self.assertIsInstance(token, expected[0])
            self.assertIsInstance(token.value, expected[1])
            self.assertIsInstance(token.value.value, IntegerLiteral)
            self.assertEqual(token.value.value.value, 1)

    def test_group_expressions(self):
        text = "print 2 * (3 + 4);"
        token = self.parse(text)[0]
        self.assertIsInstance(token, PrintStatement)
        self.assertIsInstance(token.value, BinOp)
        self.assertIsInstance(token.value.left, IntegerLiteral)
        self.assertEqual(token.value.left.value, 2)
        self.assertIsInstance(token.value.right, BinOp)
        self.assertIsInstance(token.value.right.left, IntegerLiteral)
        self.assertEqual(token.value.right.left.value, 3)
        self.assertIsInstance(token.value.right.right, IntegerLiteral)
        self.assertEqual(token.value.right.right.value, 4)

    # parsetest3 ==============================================================
    def test_constant_declaration(self):
        text = "const pi = 3.14159;"
        token = self.parse(text)[0]
        self.assertIsInstance(token, ConstDeclaration)
        self.assertIsInstance(token.name, SimpleLocation)
        self.assertEqual(token.name.name, 'pi')
        self.assertIsInstance(token.value, FloatLiteral)
        self.assertEqual(token.value.value, 3.14159)

    def test_variable_declarations(self):
        text = ("var x int;\n"
                "var y int = 23 * 45;\n")
        token1, token2 = self.parse(text)
        self.assertIsInstance(token1, VarDeclaration)
        self.assertIsInstance(token1.name, SimpleLocation)
        self.assertIsInstance(token1.datatype, SimpleType)
        self.assertEqual(token1.datatype.name, 'int')
        self.assertIsNone(token1.value)
        self.assertIsInstance(token2, VarDeclaration)
        self.assertIsInstance(token2.name, SimpleLocation)
        self.assertIsInstance(token2.datatype, SimpleType)
        self.assertEqual(token2.datatype.name, 'int')
        self.assertIsInstance(token2.value, BinOp)

    # parsetest4 ==============================================================
    def test_location(self):
        text = ("print 1 + x;\n"
                "x = 1 + 2;\n")
        token1, token2 = self.parse(text)
        self.assertIsInstance(token1, PrintStatement)
        self.assertIsInstance(token1.value, BinOp)
        self.assertIsInstance(token1.value.right, ReadLocation)
        self.assertEqual(token1.value.right.location.name, 'x')
        self.assertIsInstance(token2, Assignment)
        self.assertIsInstance(token2.name, SimpleLocation)
        self.assertEqual(token2.name.name, 'x')

    # parsetest5 ==============================================================
    def test_precedence(self):
        text = ("print 2 * 3 + 4;\n"
                "print 2 + 3 * 4;\n")
        token1, token2 = self.parse(text)
        self.assertIsInstance(token1.value, BinOp)
        self.assertEqual(token1.value.op, '+')
        self.assertIsInstance(token1.value.left, BinOp)
        self.assertEqual(token1.value.left.op, '*')
        self.assertIsInstance(token2.value, BinOp)
        self.assertEqual(token2.value.op, '+')
        self.assertIsInstance(token2.value.right, BinOp)
        self.assertEqual(token2.value.right.op, '*')

    # parsetest6 ==============================================================
    def test_line_number(self):
        text = ("print 1 +\n"
                "      2 *\n"
                "      3;\n"
                "\n"
                "var x int;\n"
                "const pi = 3.14159;\n"
                "x = 2 + 4;\n")
        for token, lineno in zip(self.parse(text), (1, 5, 6, 7)):
            self.assertEqual(token.lineno, lineno)

def mock_print(*args, **kwargs):
    import sys
    if len(kwargs) == 0:
        sys.stderr.write(str(*args) + '\n')
    else:
        raise AssertionError(args)

