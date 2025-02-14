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

    # project6
    def test_print_boolean_literals(self):
        token1, token2 = self.parse('print true;\nprint false;')
        self.assertIsInstance(token1.value, BoolLiteral)
        self.assertEqual(token1.value.value, True)
        self.assertIsInstance(token2.value, BoolLiteral)
        self.assertEqual(token2.value.value, False)

    def test_binary_boolean_operations(self):
        text = ("print 1 < 2;\n"
                "print 1 && 2;\n")
        token1, token2 = self.parse(text)
        self.assertIsInstance(token1.value, BinOp)
        self.assertEqual(token1.value.op, '<')
        self.assertIsInstance(token2.value, BinOp)
        self.assertEqual(token2.value.op, '&&')

    def test_unary_boolean_operations(self):
        token, = self.parse("print !true;\n")
        self.assertIsInstance(token.value, UnaryOp)
        self.assertEqual(token.value.op, '!')
        self.assertIsInstance(token.value.value, BoolLiteral)
        self.assertEqual(token.value.value.value, True)

    def test_no_chained_boolean_operations(self):
        with self.assertRaises(SyntaxError):
            token, = self.parse("print 1 == 2 >= 3;\n")

    def test_chained_and_or(self):
        self.parse("print 1 < 2 || 2 < 3 || 3 < 4;\n")

    def test_assign_boolean_values(self):
        text = ("var x bool = true;\n"
                "const y = 1 < 2;\n")
        token1, token2 = self.parse(text)
        self.assertIsInstance(token1, VarDeclaration)
        self.assertIsInstance(token1.name, SimpleLocation)
        self.assertIsInstance(token1.datatype, SimpleType)
        self.assertEqual(token1.datatype.name, 'bool')
        self.assertIsInstance(token1.value, BoolLiteral)
        self.assertIsInstance(token2.value, BinOp)
        self.assertIsInstance(token2, ConstDeclaration)
        self.assertIsInstance(token2.name, SimpleLocation)
        self.assertIsInstance(token2.value, BinOp)

    def test_if_else_statement(self):
        text = """
               if 1 < 2 {
                   a = 1;
               } else {
                   a = 2;
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, IfStatement)
        self.assertIsInstance(token.condition, BinOp)
        self.assertIsInstance(token.then_block, list)
        self.assertIsInstance(token.else_block, list)

    def test_if_statement(self):
        text = """
               if 1 < 2 {
                   a = 1;
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, IfStatement)
        self.assertEqual(token.else_block, [])

    def test_while_statement(self):
        text = """
               while a > 0 {
                   a = a - 1;
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, WhileStatement)
        self.assertIsInstance(token.condition, BinOp)
        self.assertIsInstance(token.loop_block, list)

    def test_empty_if_statements(self):
        text = """
               if 1 < 2 {
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, IfStatement)
        self.assertEqual(token.then_block, [])
        self.assertEqual(token.else_block, [])

    # project8
    def test_function_statements(self):
        text = """
               func add(x int, y int) int {
                   return x + y;
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, FuncDeclaration)
        self.assertIsInstance(token.name, str)
        self.assertIsInstance(token.arguments, list)
        self.assertIsInstance(token.arguments[0], FuncArgument)
        self.assertIsInstance(token.arguments[0].name, str)
        self.assertIsInstance(token.arguments[0].datatype, SimpleType)
        self.assertIsInstance(token.datatype, SimpleType)
        self.assertIsInstance(token.body, list)
        self.assertIsInstance(token.body[-1], ReturnStatement)
        self.assertIsInstance(token.body[-1].value, BinOp)

    def test_empty_functions(self):
        text = """
               func foo(x int) int {
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, FuncDeclaration)
        self.assertEqual(token.body, [])

    def test_functions_with_empty_arguments(self):
        text = """
               func main() void {
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, FuncDeclaration)
        self.assertEqual(token.arguments, [])

    def test_empty_return(self):
        text = """
               func main() void {
                   return;
               }
               """
        token, = self.parse(text)
        self.assertIsInstance(token, FuncDeclaration)
        self.assertIsInstance(token.body[-1], ReturnStatement)
        self.assertEqual(token.body[-1].value, None)

    def test_function_call(self):
        text = """
               a = add(1, 2);
               """
        token, = self.parse(text)
        self.assertIsInstance(token, Assignment)
        self.assertIsInstance(token.value, FunctionCall)
        self.assertIsInstance(token.value.name, Location)
        self.assertEqual(token.value.name.name, 'add')
        self.assertIsInstance(token.value.arguments, list)
        self.assertEqual(token.value.arguments[0].value, 1)
        self.assertEqual(token.value.arguments[1].value, 2)

    def test_for_loop(self):
        text = """
               for var i int = 0; i < 10; i = i + 1; {
                   print i;
               }

               for i = 0; i < 10; i = i + 1; {
                   print i;
               }
               """
        token1, token2 = self.parse(text)
        self.assertIsInstance(token1, ForStatement)
        self.assertIsInstance(token1.init, VarDeclaration)
        self.assertIsInstance(token1.cond, BinOp)
        self.assertIsInstance(token1.step, Assignment)
        self.assertIsInstance(token1.body, list)
        self.assertIsInstance(token2, ForStatement)
        self.assertIsInstance(token2.init, Assignment)
        self.assertIsInstance(token2.cond, BinOp)
        self.assertIsInstance(token2.step, Assignment)
        self.assertIsInstance(token2.body, list)

def mock_print(*args, **kwargs):
    import sys
    if len(kwargs) == 0:
        sys.stderr.write(str(*args) + '\n')
    else:
        raise SyntaxError(args)

