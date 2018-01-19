from unittest import TestCase
from gone.ircode import GenerateCode
from gone.parser import parse
from gone.checker import check_program
from gone.errors import clear_errors, errors_reported

class TestIRCode(TestCase):
    def _test_code(self, source, output):
        clear_errors()
        ast = parse(source)
        check_program(ast)
        code = []
        if not errors_reported():
            visitor = GenerateCode()
            visitor.visit(ast)
            code = visitor.code
        self.assertEqual(code, output)

    def _test_functions(self, source, output):
        clear_errors()
        ast = parse(source)
        check_program(ast)
        functions = []
        if not errors_reported():
            visitor = GenerateCode()
            visitor.visit(ast)
            functions_list = visitor.functions
        for function in functions_list:
            functions.append((function.name, function.body))
        self.assertEqual(functions, output)

    # irtest0
    def test_simple_literals(self):
        source = """
                 print 3;
                 print 3.5;
                 print 'a';
                 """
        output = [('MOVI', 3, 'R1'),
                  ('PRINTI', 'R1'),
                  ('MOVF', 3.5, 'R2'),
                  ('PRINTF', 'R2'),
                  ('MOVB', 97, 'R3'),
                  ('PRINTB', 'R3')]
        self._test_code(source, output)

    # irtest1
    def test_binary_operations(self):
        source = """
                 print (3 + 4*5 - 6) / 7;
                 print (3.0 + 4.0*5.0 - 6.0) / 7.0;
                 """
        output = [('MOVI', 3, 'R1'),
                  ('MOVI', 4, 'R2'),
                  ('MOVI', 5, 'R3'),
                  ('MULI', 'R2', 'R3', 'R4'),
                  ('ADDI', 'R1', 'R4', 'R5'),
                  ('MOVI', 6, 'R6'),
                  ('SUBI', 'R5', 'R6', 'R7'),
                  ('MOVI', 7, 'R8'),
                  ('DIVI', 'R7', 'R8', 'R9'),
                  ('PRINTI', 'R9'),
                  ('MOVF', 3.0, 'R10'),
                  ('MOVF', 4.0, 'R11'),
                  ('MOVF', 5.0, 'R12'),
                  ('MULF', 'R11', 'R12', 'R13'),
                  ('ADDF', 'R10', 'R13', 'R14'),
                  ('MOVF', 6.0, 'R15'),
                  ('SUBF', 'R14', 'R15', 'R16'),
                  ('MOVF', 7.0, 'R17'),
                  ('DIVF', 'R16', 'R17', 'R18'),
                  ('PRINTF', 'R18')] 
        self._test_code(source, output)

    # irtest2
    def test_unary_operations(self):
        source = """
                 print -(1+2);
                 print +(3+4);
                 print -(5.0+6.0);
                 print +(7.0+8.0);
                 """
        output = [('MOVI', 1, 'R1'),
                  ('MOVI', 2, 'R2'),
                  ('ADDI', 'R1', 'R2', 'R3'),
                  ('MOVI', 0, 'R4'),
                  ('SUBI', 'R4', 'R3', 'R5'),
                  ('PRINTI', 'R5'),
                  ('MOVI', 3, 'R6'),
                  ('MOVI', 4, 'R7'),
                  ('ADDI', 'R6', 'R7', 'R8'),
                  ('PRINTI', 'R8'),
                  ('MOVF', 5.0, 'R9'),
                  ('MOVF', 6.0, 'R10'),
                  ('ADDF', 'R9', 'R10', 'R11'),
                  ('MOVF', 0.0, 'R12'),
                  ('SUBF', 'R12', 'R11', 'R13'),
                  ('PRINTF', 'R13'),
                  ('MOVF', 7.0, 'R14'),
                  ('MOVF', 8.0, 'R15'),
                  ('ADDF', 'R14', 'R15', 'R16'),
                  ('PRINTF', 'R16')]
        self._test_code(source, output)

    # irtest3
    def test_constant_declaration(self):
        source = """
                 const x = 2;
                 const pi = 3.14159;
                 const a = 'a';

                 print x;
                 print pi;
                 print a;
                 """
        output = [('MOVI', 2, 'R1'),
                  ('VARI', 'x'),
                  ('STOREI', 'R1', 'x'),
                  ('MOVF', 3.14159, 'R2'),
                  ('VARF', 'pi'),
                  ('STOREF', 'R2', 'pi'),
                  ('MOVB', 97, 'R3'),
                  ('VARB', 'a'),
                  ('STOREB', 'R3', 'a'),
                  ('LOADI', 'x', 'R4'),
                  ('PRINTI', 'R4'),
                  ('LOADF', 'pi', 'R5'),
                  ('PRINTF', 'R5'),
                  ('LOADB', 'a', 'R6'),
                  ('PRINTB', 'R6')]
        self._test_code(source, output)

    # irtest4
    def test_variable_declarations_and_assignment(self):
        source = """
                 var x int = 42;
                 var y int;
                 y = x + 10;

                 var pi float = 3.14159;
                 var z float;
                 z = 2.0 * pi;

                 var a char = 'a';
                 var b char;
                 b = a;
                 """
        output = [('MOVI', 42, 'R1'),
                  ('VARI', 'x'),
                  ('STOREI', 'R1', 'x'),
                  ('VARI', 'y'),
                  ('LOADI', 'x', 'R2'),
                  ('MOVI', 10, 'R3'),
                  ('ADDI', 'R2', 'R3', 'R4'),
                  ('STOREI', 'R4', 'y'),
                  ('MOVF', 3.14159, 'R5'),
                  ('VARF', 'pi'),
                  ('STOREF', 'R5', 'pi'),
                  ('VARF', 'z'),
                  ('MOVF', 2.0, 'R6'),
                  ('LOADF', 'pi', 'R7'),
                  ('MULF', 'R6', 'R7', 'R8'),
                  ('STOREF', 'R8', 'z'),
                  ('MOVB', 97, 'R9'),
                  ('VARB', 'a'),
                  ('STOREB', 'R9', 'a'),
                  ('VARB', 'b'),
                  ('LOADB', 'a', 'R10'),
                  ('STOREB', 'R10', 'b')]
        self._test_code(source, output)

    # project6
    def test_boolean_literals(self):
        source = """
                 print true;
                 print false;
                 """
        output = [('MOVI', 1, 'R1'),
                  ('PRINTI', 'R1'),
                  ('MOVI', 0, 'R2'),
                  ('PRINTI', 'R2')]
        self._test_code(source, output)

    def test_boolean_binary_operations(self):
        source = """
                 print 3 < 4;
                 print (3.0 > 6.0) || (5 >= 2);
                 """
        output = [('MOVI', 3, 'R1'),
                  ('MOVI', 4, 'R2'),
                  ('CMPI', '<', 'R1', 'R2', 'R3'),
                  ('PRINTI', 'R3'),
                  ('MOVF', 3.0, 'R4'),
                  ('MOVF', 6.0, 'R5'),
                  ('CMPF', '>', 'R4', 'R5', 'R6'),
                  ('MOVI', 5, 'R7'),
                  ('MOVI', 2, 'R8'),
                  ('CMPI', '>=', 'R7', 'R8', 'R9'),
                  ('OR', 'R6', 'R9', 'R10'),
                  ('PRINTI', 'R10')]
        self._test_code(source, output)

    def test_boolean_unary_operations(self):
        source = """
                 print !true;
                 """
        output = [('MOVI', 1, 'R1'),
                  ('MOVI', 1, 'R2'),
                  ('SUBI', 'R2', 'R1', 'R3'),
                  ('PRINTI', 'R3')]
        self._test_code(source, output)

    def test_boolean_variables_and_constants(self):
        source = """
                 const x = true;
                 var y bool = false;
                 var z bool;
                 z = x || y;
                 """
        output = [('MOVI', 1, 'R1'),
                  ('VARI', 'x'),
                  ('STOREI', 'R1', 'x'),
                  ('MOVI', 0, 'R2'),
                  ('VARI', 'y'),
                  ('STOREI', 'R2', 'y'),
                  ('VARI', 'z'),
                  ('LOADI', 'x', 'R3'),
                  ('LOADI', 'y', 'R4'),
                  ('OR', 'R3', 'R4', 'R5'),
                  ('STOREI', 'R5', 'z')]
        self._test_code(source, output)

    # project7
    def test_if_else_statements(self):
        source = """
                 var a int;
                 if 3 < 4 {
                     a = 1;
                 } else {
                     a = 2;
                 }
                 """
        output = [('VARI', 'a'),
                  ('MOVI', 3, 'R1'),
                  ('MOVI', 4, 'R2'),
                  ('CMPI', '<', 'R1', 'R2', 'R3'),
                  ('CBRANCH', 'R3', 'B1', 'B2'),
                  ('LABEL', 'B1'),
                  ('MOVI', 1, 'R4'),
                  ('STOREI', 'R4', 'a'),
                  ('BRANCH', 'B3'),
                  ('LABEL', 'B2'),
                  ('MOVI', 2, 'R5'),
                  ('STOREI', 'R5', 'a'),
                  ('BRANCH', 'B3'),
                  ('LABEL', 'B3')]
        self._test_code(source, output)

    def test_if_statements(self):
        source = """
                 var a int;
                 if 3 < 4 {
                     a = 1;
                 }
                 """
        output = [('VARI', 'a'),
                  ('MOVI', 3, 'R1'),
                  ('MOVI', 4, 'R2'),
                  ('CMPI', '<', 'R1', 'R2', 'R3'),
                  ('CBRANCH', 'R3', 'B1', 'B2'),
                  ('LABEL', 'B1'),
                  ('MOVI', 1, 'R4'),
                  ('STOREI', 'R4', 'a'),
                  ('BRANCH', 'B3'),
                  ('LABEL', 'B2'),
                  ('BRANCH', 'B3'),
                  ('LABEL', 'B3')]
        self._test_code(source, output)

    def test_while_statements(self):
        source = """
                 var a int = 10;
                 while a > 0 {
                     a = a - 1;
                 }
                 """
        output = [('MOVI', 10, 'R1'),
                  ('VARI', 'a'),
                  ('STOREI', 'R1', 'a'),
                  ('BRANCH', 'B1'),
                  ('LABEL', 'B1'),
                  ('LOADI', 'a', 'R2'),
                  ('MOVI', 0, 'R3'),
                  ('CMPI', '>', 'R2', 'R3', 'R4'),
                  ('CBRANCH', 'R4', 'B2', 'B3'),
                  ('LABEL', 'B2'),
                  ('LOADI', 'a', 'R5'),
                  ('MOVI', 1, 'R6'),
                  ('SUBI', 'R5', 'R6', 'R7'),
                  ('STOREI', 'R7', 'a'),
                  ('BRANCH', 'B1'),
                  ('LABEL', 'B3')]
        self._test_code(source, output)

    def test_function_declaration(self):
        source = """
                 func add(x int, y int) int {
                     return x + y;
                 }
                 """
        output = [('_init', []),
                  ('add', [('ALLOCI', 'x'),
                           ('STOREI', 'R1', 'x'),
                           ('ALLOCI', 'y'),
                           ('STOREI', 'R2', 'y'),
                           ('LOADI', 'x', 'R3'),
                           ('LOADI', 'y', 'R4'),
                           ('ADDI', 'R3', 'R4', 'R5'),
                           ('RET', 'R5')])]
        self._test_functions(source, output)

    def test_define_global_and_local_variables(self):
        source = """
                 func foo(x int) int {
                     var y int;
                     return x + y;
                 }
                 const x = 5;
                 """
        output = [('_init', [('MOVI', 5, 'R5'),
                             ('VARI', 'x'),
                             ('STOREI', 'R5', 'x')]),
                  ('foo', [('ALLOCI', 'x'),
                           ('STOREI', 'R1', 'x'),
                           ('ALLOCI', 'y'),
                           ('LOADI', 'x', 'R2'),
                           ('LOADI', 'y', 'R3'),
                           ('ADDI', 'R2', 'R3', 'R4'),
                           ('RET', 'R4')])]
        self._test_functions(source, output)

    def test_function_call(self):
        self.maxDiff = None
        source = """
                 func add(x int, y int) int { return x + y; }
                 var x int = add(1, 2);
                 """
        output = [('_init', [('MOVI', 1, 'R6'),
                             ('MOVI', 2, 'R7'),
                             ('CALL', 'add', 'R6', 'R7', 'R8'),
                             ('VARI', 'x'),
                             ('STOREI', 'R8', 'x')]),
                  ('add', [('ALLOCI', 'x'),
                           ('STOREI', 'R1', 'x'),
                           ('ALLOCI', 'y'),
                           ('STOREI', 'R2', 'y'),
                           ('LOADI', 'x', 'R3'),
                           ('LOADI', 'y', 'R4'),
                           ('ADDI', 'R3', 'R4', 'R5'),
                           ('RET', 'R5')])]
        self._test_functions(source, output)

