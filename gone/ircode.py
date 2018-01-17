# gone/ircode.py
'''
Project 4
=========
In this project, you are going to turn the AST into an intermediate
machine code based on 3-address code. There are a few important parts
you'll need to make this work.  Please read carefully before
beginning:

A "Virtual" Machine
===================
A CPU typically consists of registers and a small set of basic opcodes
for performing mathematical calculations, loading/storing values from
memory, and basic control flow (branches, jumps, etc.).  For example,
suppose you want to evaluate an operation like this:

    a = 2 + 3 * 4 - 5

On a CPU, it might be decomposed into low-level instructions like this:

    MOVI   #2, R1
    MOVI   #3, R2
    MOVI   #4, R3
    MULI   R2, R3, R4
    ADDI   R4, R1, R5
    MOVI   #5, R6
    SUBI   R5, R6, R7
    STOREI R7, "a"

Each instruction represents a single operation such as add, multiply, etc.
There are always two input operands and a destination.  

CPUs also feature a small set of core datatypes such as integers,
bytes, and floats. There are dedicated instructions for each type.
For example:

    ADDI   R1, R2, R3        ; Integer add
    ADDF   R4, R5, R6        ; Float add

There is often a disconnect between the types used in the source
programming language and the generated IRCode.  For example, a target
machine might only have integers and floats.  To represent a value
such as a boolean, you have to represent it as one of the native types
such as an integer.   This is an implementation detail that users
won't worry about (they'll never see it, but you'll have to worry
about it in the compiler).

Here is an instruction set specification for our IRCode:

    MOVI   value, target       ;  Load a literal integer
    VARI   name                ;  Declare an integer variable 
    ALLOCI name                ;  Allocate an integer variabe on the stack
    LOADI  name, target        ;  Load an integer from a variable
    STOREI target, name        ;  Store an integer into a variable
    ADDI   r1, r2, target      ;  target = r1 + r2
    SUBI   r1, r2, target      ;  target = r1 - r2
    MULI   r1, r2, target      ;  target = r1 * r2
    DIVI   r1, r2, target      ;  target = r1 / r2
    PRINTI source              ;  print source  (debugging)
    CMPI   op, r1, r2, target  ;  Compare r1 op r2 -> target
    AND    r1, r2, target      :  target = r1 & r2
    OR     r1, r2, target      :  target = r1 | r2
    XOR    r1, r2, target      :  target = r1 ^ r2
    ITOF   r1, target          ;  target = float(r1)

    MOVF   value, target       ;  Load a literal float
    VARF   name                ;  Declare a float variable 
    ALLOCF name                ;  Allocate a float variable on the stack
    LOADF  name, target        ;  Load a float from a variable
    STOREF target, name        ;  Store a float into a variable
    ADDF   r1, r2, target      ;  target = r1 + r2
    SUBF   r1, r2, target      ;  target = r1 - r2
    MULF   r1, r2, target      ;  target = r1 * r2
    DIVF   r1, r2, target      ;  target = r1 / r2
    PRINTF source              ;  print source (debugging)
    CMPF   op, r1, r2, target  ;  r1 op r2 -> target
    FTOI   r1, target          ;  target = int(r1)

    MOVB   value, target       ; Load a literal byte
    VARB   name                ; Declare a byte variable
    ALLOCB name                ; Allocate a byte variable
    LOADB  name, target        ; Load a byte from a variable
    STOREB target, name        ; Store a byte into a variable
    PRINTB source              ; print source (debugging)
    BTOI   r1, target          ; Convert a byte to an integer
    ITOB   r2, target          ; Truncate an integer to a byte
    CMPB   op, r1, r2, target  ; r1 op r2 -> target

There are also some control flow instructions

    LABEL  name                  ; Declare a label
    BRANCH label                 ; Unconditionally branch to label
    CBRANCH test, label1, label2 ; Conditional branch to label1 or label2 depending on test being 0 or not
    CALL   name, arg0, arg1, ... argN, target    ; Call a function name(arg0, ... argn) -> target
    RET    r1                    ; Return a result from a function

Single Static Assignment
========================
On a real CPU, there are a limited number of CPU registers.
In our virtual memory, we're going to assume that the CPU
has an infinite number of registers available.  Moreover,
we'll assume that each register can only be assigned once.
This particular style is known as Static Single Assignment (SSA).
As you generate instructions, you'll keep a running counter
that increments each time you need a temporary variable.
The example in the previous section illustrates this.

Your Task
=========
Your task is as follows: Write a AST Visitor() class that takes a
program and flattens it to a single sequence of SSA code instructions
represented as tuples of the form 

       (operation, operands, ..., destination)

Testing
=======
The files Tests/irtest0-5.g contain some input text along with
sample output. Work through each file to complete the project.
'''

from . import ast

class GenerateCode(ast.NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        # counter for registers
        self.register_count = 0

        # The generated code (list of tuples)
        self.code = []

    def new_register(self):
         '''
         Creates a new temporary register
         '''
         self.register_count += 1
         return f'R{self.register_count}'

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.code list.
    #
    # A few sample methods follow.  You may have to adjust depending
    # on the names and structure of your AST nodes.

    def visit_IntegerLiteral(self, node):
        self._literal(node)

    def visit_FloatLiteral(self, node):
        self._literal(node)

    def visit_CharLiteral(self, node):
        self._literal(node)

    def visit_BoolLiteral(self, node):
        self._literal(node)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        target = self.new_register()
        code = _build_instruction_name(node.op, node.left.type)
        inst = (*code, node.left.register, node.right.register, target)
        self.code.append(inst)
        node.register = target

    def visit_UnaryOp(self, node):
        self.visit(node.value)
        if node.op == '-':
            # put zero on stack
            zero_target = self.new_register()
            zero_code = 'MOV' + _type_char(node.type)
            zero_inst = (zero_code, 0 if node.type == 'int' else 0.0, zero_target)
            self.code.append(zero_inst)
            # do subtraction
            target = self.new_register()
            code = _build_instruction_name(node.op, node.type)
            inst = (*code, zero_target, node.value.register, target)
            self.code.append(inst)
        elif node.op == '!':
            one_target = self.new_register()
            self.code.append(('MOVI', 1, one_target))
            target = self.new_register()
            self.code.append(('SUBI', one_target, node.value.register, target))
        else:
            # do addition
            target = node.value.register
        node.register = target

    def visit_PrintStatement(self, node):
        self.visit(node.value)
        code = 'PRINT' + _type_char(node.value.type)
        inst = (code, node.value.register)
        self.code.append(inst)

    def visit_ConstDeclaration(self, node):
        self.visit(node.value)
        self._declare(node)
        self._store(node)

    def visit_VarDeclaration(self, node):
        self.visit(node.value)
        self._declare(node)
        if node.value is not None:
            self._store(node)

    def visit_Assignment(self, node):
        self.visit(node.value)
        self._store(node)

    def visit_ReadLocation(self, node):
        target = self.new_register()
        code = 'LOAD' + _type_char(node.type)
        inst = (code, node.location.name, target)
        self.code.append(inst)
        node.register = target

    def _literal(self, node):
        target = self.new_register()
        code = 'MOV' + _type_char(node.type)
        if node.type in {'int', 'float'}:
            value = node.value
        elif node.type == 'char':
            value = ord(node.value)
        else:
            value = 1 if node.value else 0
        self.code.append((code, value, target))
        node.register = target

    def _declare(self, node):
        self.code.append(('VAR' + _type_char(node.type), node.name.name))

    def _store(self, node):
        code = 'STORE' + _type_char(node.value.type)
        inst = (code, node.value.register, node.name.name)
        self.code.append(inst)

def _type_char(type_name):
    if type_name in {'int', 'float'}:
        return type_name[0].upper()
    elif type_name == 'char':
        return 'B'
    return 'I'

def _build_instruction_name(op_name, type_name):
    op_table = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
    and_or = {'&&': 'AND', '||': 'OR'}
    rel_table = {op: 'CMP' for op in ('<', '>', '<=', '>=', '==', '!=')}
    if op_name in op_table:
        return (op_table[op_name] + _type_char(type_name),)
    elif op_name in rel_table:
        return (rel_table[op_name] + _type_char(type_name), op_name)
    elif op_name in and_or:
        return (and_or[op_name],)
    else:
        raise RuntimeError(f'Unknown operation {op}')


# ----------------------------------------------------------------------
#                          TESTING/MAIN PROGRAM
#
# Note: Some changes will be required in later projects.
# ----------------------------------------------------------------------

def compile_ircode(source):
    '''
    Generate intermediate code from source.
    '''
    from .parser import parse
    from .checker import check_program
    from .errors import errors_reported

    ast = parse(source)
    check_program(ast)

    # If no errors occurred, generate code
    if not errors_reported():
        gen = GenerateCode()
        gen.visit(ast)
        return gen.code    
    else:
        return []

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.ircode filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)

    for instr in code:
        print(instr)

if __name__ == '__main__':
    main()

