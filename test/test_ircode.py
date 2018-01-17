from unittest import TestCase
from gone.ircode import compile_ircode
from gone.errors import clear_errors

class TestIRCode(TestCase):
    def _test(self, source, output):
        clear_errors()
        code = compile_ircode(source)
        self.assertEqual(code, output)

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
        self._test(source, output)

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
        self._test(source, output)

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
        self._test(source, output)

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
        self._test(source, output)

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
        self._test(source, output)

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
        self._test(source, output)

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
        self._test(source, output)

    def test_boolean_unary_operations(self):
        source = """
                 print !true;
                 """
        output = [('MOVI', 1, 'R1'),
                  ('MOVI', 1, 'R2'),
                  ('SUBI', 'R2', 'R1', 'R3'),
                  ('PRINTI', 'R3')]
        self._test(source, output)

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
        self._test(source, output)

