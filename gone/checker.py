# gone/checker.py
'''
*** Do not start this project until you have fully completed Exercise 3. ***

Overview
--------
In this project you need to perform semantic checks on your program.
This problem is multifaceted and complicated.  To make it somewhat
less brain exploding, you need to take it slow and in small parts.
The basic gist of what you need to do is as follows:

1.  Names and symbols:

    All identifiers must be defined before they are used.  This
    includes variables, constants, and typenames.  For example, this
    kind of code generates an error:

       a = 3;              // Error. 'a' not defined.
       var a int;

2.  Types of literals and constants

    All literal symbols are implicitly typed and must be assigned a
    type of "int", "float", or "char".  This type is used to set
    the type of constants.  For example:

       const a = 42;         // Type "int"
       const b = 4.2;        // Type "float"
       const c = 'a';        // Type "char""

3.  Operator type checking

    Binary operators only operate on operands of a compatible type.
    Otherwise, you get a type error.  For example:

        var a int = 2;
        var b float = 3.14;

        var c int = a + 3;    // OK
        var d int = a + b;    // Error.  int + float
        var e int = b + 4.5;  // Error.  int = float

    In addition, you need to make sure that only supported 
    operators are allowed.  For example:

        var a char = 'a';        // OK
        var b char = 'a' + 'b';  // Error (unsupported op +)

4.  Assignment.

    The left and right hand sides of an assignment operation must be
    declared as the same type.

        var a int;
        a = 4 + 5;     // OK
        a = 4.5;       // Error. int = float

    Values can only be assigned to variable declarations, not
    to constants.

        var a int;
        const b = 42;

        a = 37;        // OK
        b = 37;        // Error. b is const

Implementation Strategy:
------------------------
You're going to use the NodeVisitor class defined in gone/ast.py to
walk the parse tree.   You will be defining various methods for
different AST node types.  For example, if you have a node BinOp,
you'll write a method like this:

      def visit_BinOp(self, node):
          ...

To start, make each method simply print out a message:

      def visit_BinOp(self, node):
          print('visit_BinOp:', node)
          self.visit(node.left)
          self.visit(node.right)

This will at least tell you that the method is firing.  Try some
simple code examples and make sure that all of your methods
are actually running when you walk the parse tree.

Testing
-------
The files Tests/checktest0-7.g contain different things you need
to check for.  Specific instructions are given in each test file.

General thoughts and tips
-------------------------
The main thing you need to be thinking about with checking is program
correctness.  Does this statement or operation that you're looking at
in the parse tree make sense?  If not, some kind of error needs to be
generated.  Use your own experiences as a programmer as a guide (think
about what would cause an error in your favorite programming
language).

One challenge is going to be the management of many fiddly details. 
You've got to track symbols, types, and different sorts of capabilities.
It's not always clear how to best organize all of that.  So, expect to
fumble around a bit at first.
'''

from .errors import error
from .ast import *
from .typesys import check_binop, check_unaryop, builtin_types
from collections import ChainMap

class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    '''
    def __init__(self):
        # Initialize the symbol table
        self.symbols = ChainMap({}, {})

    def visit_ConstDeclaration(self, node):
        # For a declaration, you'll need to check that it isn't already defined.
        # You'll put the declaration into the symbol table so that it can be
        # looked up later
        name = node.name.name
        node.writeable = False
        if name in builtin_types:
            error(node.lineno, f'NameError: cannot declare variable with name {name}')
            return
        elif name not in self.symbols:
            self.symbols[name] = node
            self.visit(node.value)
            node.type = node.value.type
        else:
            error(node.lineno, f'NameError: constant "{name}" already defined.')

    def visit_VarDeclaration(self, node):
        name = node.name.name
        node.writeable = True
        if name in builtin_types:
            error(node.lineno, f'NameError: cannot declare variable with name {name}')
            return
        elif name not in self.symbols:
            self.symbols[name] = node
            self.visit(node.datatype)
            node.type = node.datatype.type
        else:
            error(node.lineno, f'NameError: variable "{name}" already defined.')
            return
        if node.value is not None:
            self.visit(node.value)
            if node.type != node.value.type:
                error(node.lineno, f'TypeError: assigning type {node.value.type} to "{node.name.name}" of type {node.type}')

    def visit_Assignment(self, node):
        node.name.usage = 'write'
        self.visit(node.name)
        self.visit(node.value)
        if node.name.type != node.value.type:
            error(node.lineno, f'TypeError: assigning type {node.value.type} to "{node.name.name}" of type {node.name.type}')

    def visit_IfStatement(self, node):
        self.visit(node.condition)
        if node.condition.type != 'bool':
            error(node.lineno, 'TypeError: if-statement condition is not a boolean')
            return
        self.visit(node.then_block)
        self.visit(node.else_block)

    def visit_WhileStatement(self, node):
        self.visit(node.condition)
        if node.condition.type != 'bool':
            error(node.lineno, 'TypeError: while-statement condition is not a boolean')
            return
        self.visit(node.loop_block)

    def visit_FuncStatement(self, node):
        self.symbols[node.name] = node
        self.visit(node.datatype)
        node.type = node.datatype.type
        self.symbols = self.symbols.new_child()
        self.visit(node.arguments)

        returned = False
        for statement in node.body:
            self.visit(statement)
            if isinstance(statement, ReturnStatement):
                returned = True
                if statement.type != node.type:
                    error(statement.lineno, f'TypeError: returning {statement.type} instead of {node.type}')
                    node.type = 'error'
                break
        if not returned:
            if node.type != 'void':
                error(node.lineno, f'TypeError: missing return statement')
                node.type = 'error'
            else:
                node.type = 'void'
        self.symbols = self.symbols.parents

    def visit_FuncArgument(self, node):
        self.symbols[node.name] = node
        self.visit(node.datatype)
        node.type = node.datatype.type

    def visit_ReturnStatement(self, node):
        self.visit(node.value)
        node.type = node.value.type if node.value is not None else 'void'

    def visit_PrintStatement(self, node):
        self.visit(node.value)

    def visit_SimpleLocation(self, node):
        # A location represents a place where you can read/write a value.
        # You'll need to consult the symbol table to find out information about it
        try:
            symbol = self.symbols[node.name]
            node.type = symbol.type
            if node.usage == 'write' and not symbol.writeable:
                error(node.lineno, f'TypeError: cannot assign to constant "{node.name}"')
        except KeyError:
            error(node.lineno, f'NameError: symbol "{node.name}" undefined.')
            node.type = 'error'

    def visit_ReadLocation(self, node):
        node.location.usage = 'read'
        self.visit(node.location)
        node.type = node.location.type

    def visit_IntegerLiteral(self, node):
        # For literals, you'll need to assign a type to the node and allow it to
        # propagate.  This type will work it's way through various operators
        node.type = 'int'

    def visit_FloatLiteral(self, node):
        node.type = 'float'

    def visit_CharLiteral(self, node):
        node.type = 'char'

    def visit_BoolLiteral(self, node):
        node.type = 'bool'

    def visit_BinOp(self, node):
        # For operators, you need to visit each operand separately.  You'll
        # then need to make sure the types and operator are all compatible.
        self.visit(node.left)
        self.visit(node.right)
        node.type = check_binop(node.left.type, node.op, node.right.type)
        if node.type == 'error':
            msg = f'TypeError: performing "{node.op}" on {node.left.type} and {node.right.type}'
            error(node.lineno, msg)

    def visit_UnaryOp(self, node):
        self.visit(node.value)
        node.type = check_unaryop(node.op, node.value.type)
        if node.type == 'error':
            msg = f'TypeError: performing "{node.op}" on {node.value.type}'
            error(node.lineno, msg)

    def visit_SimpleType(self, node):
        # Associate a type name such as "int" with a Type object
        if node.name in builtin_types:
            node.type = node.name
        else:
            error(node.lineno, f'TypeError: unknown type "{node.name}"')
            node.type = 'error'


# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)

def main():
    '''
    Main program. Used for testing
    '''
    import sys
    from .parser import parse

    if len(sys.argv) < 2:
        sys.stderr.write('Usage: python3 -m gone.checker filename\n')
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)
    if '--show-types' in sys.argv:
        for depth, node in flatten(ast):
            print('%s: %s%s type: %s' % (getattr(node, 'lineno', None), ' '*(4*depth), node,
                                         getattr(node, 'type', None)))

if __name__ == '__main__':
    main()

