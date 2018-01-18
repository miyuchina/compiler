from unittest import TestCase
from unittest.mock import patch
from gone.checker import CheckProgramVisitor
from gone.parser import parse

class TestChecker(TestCase):
    def setUp(self):
        self.checker = CheckProgramVisitor()
        self.check_program = lambda source: self.checker.visit(parse(source))
        self.captured_output = []
        self.patcher = patch('builtins.print', self.mock_print)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    # checktest0
    def test_track_symbols(self):
        source = ("const pi = 3.14159;\n"
                  "var x int;\n"
                  "\n"
                  "print pi;\n"
                  "print x;\n"
                  "print y;\n"
                  "\n"
                  "x = 45;\n"
                  "z = 13;\n")
        self.check_program(source)
        for symbol in ('pi', 'x'):
            self.assertTrue(symbol in self.checker.symbols)
        expected_output = [('6: NameError: symbol "y" undefined.',),
                           ('9: NameError: symbol "z" undefined.',),
                           ('9: TypeError: assigning type int to "z" of type error',)]
        self.assertEqual(expected_output, self.captured_output)

    # checktest1
    def test_redefinition(self):
        source = ("const a = 2;        // OK\n"
                  "var x int;          // OK\n"
                  "\n"
                  "var a float;        // ERROR. a previously defined\n"
                  "const x = 3;        // ERROR. x previously defined\n")
        self.check_program(source)
        expected_output = [('4: NameError: variable "a" already defined.',),
                           ('5: NameError: constant "x" already defined.',)]
        self.assertEqual(expected_output, self.captured_output)

    # checktest2
    def test_read_write(self):
        source = ("const a = 2;\n"
                  "a = 4;              // ERROR. a is constant\n"
                  "print a;            // OK. Reading\n"
                  "\n"
                  "var b int;\n"
                  "b = 5;              // OK. Storing a value\n"
                  "print b;            // OK. Reading\n")
        self.check_program(source)
        expected_output = [('2: TypeError: cannot assign to constant "a"',),]
        self.assertEqual(expected_output, self.captured_output)

    # checktest5
    def test_operation_types(self):
        source = ("print 2 + 3.5;    // ERROR\n"
                  "print 2.0 + 3;    // ERROR\n"
                  "\n"
                  "print 'h' + 'w';  // ERROR\n"
                  "print 'h' - 'w';\n"
                  "print 'h' * 'w';\n"
                  "print 'h' / 'w';\n"
                  "print -'h';\n"
                  "print +'h';\n")
        self.check_program(source)
        expected_output = [('1: TypeError: performing "+" on int and float',),
                           ('2: TypeError: performing "+" on float and int',),
                           ('4: TypeError: performing "+" on char and char',),
                           ('5: TypeError: performing "-" on char and char',),
                           ('6: TypeError: performing "*" on char and char',),
                           ('7: TypeError: performing "/" on char and char',),
                           ('8: TypeError: performing "-" on char',),
                           ('9: TypeError: performing "+" on char',)]
        self.assertEqual(expected_output, self.captured_output)

    # checktest6
    def test_declare_types(self):
        source = ("const a = 1;\n"
                  "var x int;\n"
                  "\n"
                  "x = a + 2;        // OK\n"
                  "x = 3.5;          // Error\n"
                  "\n"
                  "var y int = 3.5;  // Error\n"
                  "var z spam;       // Error. Unknown type name 'spam'\n")
        self.check_program(source)
        expected_output = [('5: TypeError: assigning type float to "x" of type int',),
                           ('7: TypeError: assigning type float to "y" of type int',),
                           ('8: TypeError: unknown type "spam"',)]
        self.assertEqual(expected_output, self.captured_output)

    # checktest7
    def test_builtin_types(self):
        source = ("print float;      // ERROR. float is not a valid expression\n"
                  "int = 3;          // ERROR. int is not a valid location\n"
                  "var int float;    // ERROR. int previously declared (as a type)\n")
        self.check_program(source)
        expected_output = [('1: NameError: symbol "float" undefined.',),
                           ('2: NameError: symbol "int" undefined.',),
                           ('2: TypeError: assigning type int to "int" of type error',),
                           ('3: NameError: cannot declare variable with name int',)]
        self.assertEqual(expected_output, self.captured_output)

    # project6
    def test_boolean_types(self):
        source = ("var a bool = true;\n"
                  "a = 1;\n")
        self.check_program(source)
        expected_output = [('2: TypeError: assigning type int to "a" of type bool',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_boolean_binary_operation_types(self):
        source = ("var a int = 3;\n"
                  "var b int = 4;\n"
                  "var c bool = (a != 0) || (b != 0);\n"
                  "var d bool = a || b;\n")
        self.check_program(source)
        expected_output = [('4: TypeError: performing "||" on int and int',),
                           ('4: TypeError: assigning type error to "d" of type bool',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_boolean_unary_operation_types(self):
        source = ("var a bool = true;\n"
                  "a = !a;\n"
                  "var b int = 3;\n"
                  "b = !b;\n")
        self.check_program(source)
        expected_output = [('4: TypeError: performing "!" on int',),
                           ('4: TypeError: assigning type error to "b" of type int',)]
        self.assertEqual(expected_output, self.captured_output)

    # project7
    def test_if_statement_types(self):
        source = ("if 2 < 3 {\n"
                  "    var a int = 3;\n"
                  "}\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_if_statement_wrong_types(self):
        source = ("if 2 + 3 {\n"
                  "    var a int = 3;\n"
                  "}\n")
        self.check_program(source)
        expected_output = [('1: TypeError: if-statement condition is not a boolean',),]
        self.assertEqual(expected_output, self.captured_output)

    def test_while_statement_types(self):
        source = ("while true {\n"
                  "    var a int = 1;\n"
                  "}\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_while_statement_wrong_types(self):
        source = ("while 't' {\n"
                  "    var a int = 1;\n"
                  "}\n")
        self.check_program(source)
        expected_output = [('1: TypeError: while-statement condition is not a boolean',)]
        self.assertEqual(expected_output, self.captured_output)

    # project8
    def test_correct_function_types(self):
        source = ("func add(x int, y int) int {\n"
                  "    return x + y;\n"
                  "}\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_function_wrong_local_types(self):
        source = ("func add(x int, y float) int {\n"
                  "    return x + y;\n"
                  "}\n")
        self.check_program(source)
        expected_output = [('2: TypeError: performing "+" on int and float',),
                           ('2: TypeError: returning error instead of int',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_function_wrong_return_type(self):
        source = ("func add(x float, y float) int {\n"
                  "    return x + y;\n"
                  "}\n")
        self.check_program(source)
        expected_output = [('2: TypeError: returning float instead of int',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_function_no_return(self):
        source = ("func main() void {\n"
                  "}\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_function_with_empty_return(self):
        source = ("func main() void {\n"
                  "    return;\n"
                  "}\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_wrong_function_with_empty_return(self):
        source = ("func main() int {\n"
                  "    return;\n"
                  "}\n")
        self.check_program(source)
        expected_output = [('2: TypeError: returning void instead of int',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_multiple_variable_declaration_in_functions(self):
        source = ("func foo(x int) int {\n"
                  "    var x int;\n"
                  "    return 0;\n"
                  "}\n")
        self.check_program(source)
        expected_output = [('2: NameError: variable "x" already defined.',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_global_variable_redeclared_in_function_scope(self):
        source = ("const x = 1;\n"
                  "func foo() int {\n"
                  "    var x int;\n"
                  "    return 0;\n"
                  "}\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_local_variable_redeclared_in_global_scope(self):
        source = ("func foo() int {\n"
                  "    var x int;\n"
                  "    return 0;\n"
                  "}\n"
                  "const x = 1;\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_function_call(self):
        source = ("func add(x int, y int) int {\n"
                  "    return x + y;\n"
                  "}\n"
                  "var a int = add(1, 2);\n")
        self.check_program(source)
        expected_output = []
        self.assertEqual(expected_output, self.captured_output)

    def test_undefined_function_call(self):
        source = "var a int = add(1, 2);\n"
        self.check_program(source)
        expected_output = [('1: NameError: symbol "add" undefined.',),
                           ('1: TypeError: assigning type error to "a" of type int',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_function_call_with_wrong_number_of_arguments(self):
        source = ("func add(x int, y int) int {\n"
                  "    return x + y;\n"
                  "}\n"
                  "var a int = add(1, 2, 3);\n")
        self.check_program(source)
        expected_output = [('4: TypeError: add() takes 2 arguments but 3 given',),
                           ('4: TypeError: assigning type error to "a" of type int',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_function_call_with_wrong_argument_types(self):
        source = ("func add(x int, y int) int {\n"
                  "    return x + y;\n"
                  "}\n"
                  "var a int = add(1, 2.0);\n")
        self.check_program(source)
        expected_output = [('4: TypeError: add() expecting (\'int\', \'int\'), got (\'int\', \'float\')',),
                           ('4: TypeError: assigning type error to "a" of type int',)]
        self.assertEqual(expected_output, self.captured_output)

    def test_calling_a_non_function(self):
        source = ("var add void;\n"
                  "var a int = add(1, 2);\n")
        self.check_program(source)
        expected_output = [('2: TypeError: "add" is not callable.',),
                           ('2: TypeError: assigning type error to "a" of type int',)]
        self.assertEqual(expected_output, self.captured_output)

    def mock_print(self, *args, **kwargs):
        self.captured_output.append(args)

