# Compiler

This repository implements a compiler for a subset of the Go programming language ("gone").

## Usage

This compiler requires Python 3.6 or above.
To use the compiler, the following packages are required:

* A working version of Clang;
* The latest version of [Anaconda](https://www.anaconda.com) Python;
* The latest version of [llvmlite](http://llvmlite.pydata.org/en/latest/) included with Anaconda;
* The latest version of [SLY](https://github.com/dabeaz/sly), a Python parser-generator.

To verify the compiler is working, clone the repo and run:

```sh
(cd gone && make)
python3 -m gone.compile Tests/mandel.g
./a.out
```

This should create an executable `a.out` in your working directory,
and plot a Mandelbrot set on your terminal screen.

While you are in the base directory of the repo,
running

```sh
make test
```

... should run the unit tests for the compiler.
The tests covers lexing, parsing, type checking and the IR code generation;
output to LLVM IR is not unit tested.

The "gone" programming language generally follows Go's syntax.
To view `Tests/mandel.g` in vim, for example, running

```vimscript
set filetype=go
```

... should give you pretty good syntax highlighting.

## Features

Here's how to manually walk through the different compilation stages.

### lexing / tokenizing

```sh
$ python3 -m gone.tokenizer Tests/mandel.g
Token(type='CONST', value='const', lineno=3, index=16)
Token(type='ID', value='xmin', lineno=3, index=22)
Token(type='ASSIGN', value='=', lineno=3, index=27)
Token(type='MINUS', value='-', lineno=3, index=29)
Token(type='FLOAT', value='2.0', lineno=3, index=30)
# ...
```

The tokenizer outputs a stream of token objects with their respective types, values,
line numbers and indices.

### parsing

```sh
$ python3 -m gone.parser Tests/mandel.g
3: ConstDeclaration(name=SimpleLocation, value=UnaryOp)
3:     SimpleLocation(name='xmin')
3:     UnaryOp(op='-', value=FloatLiteral)
3:         FloatLiteral(value=2.0)
# ...
```

The parser takes the stream of tokens from the tokenizer,
and builds an abstract syntax tree.
The above example is the AST for the following piece of code:

```go
const xmin = -2.0;
```

Syntax errors are detected at this stage.
The grammar for constant declarations, for example, looks like this:

```
const_declaration ::== CONST location ASSIGN expression SEMI
location          ::== ID
expression        ::== MINUS INTEGER
```

If we have

```go
const xmin float = -2.0;
```

... the parser will complain:

```
1: Syntax error in input at token 'float'
```

... because constant declarations do not accept type annotations.

### type checking

```sh
$ python3 -m gone.checker Tests/mandel.g
```

Type errors, unsupported operations on types and undeclared variables
are reported at this stage.
If the input file does not contain any type errors,
the type checker will not produce any output.
If, however, we have the following code:

```go
var x int = 3.0;
print float;
int = 3;
var int float;
```

The type checker should produce the following errors:

```
1: TypeError: assigning float to variable "x" of type int.
2: NameError: symbol "float" undefined.
3: NameError: symbol "int" undefined.
4: NameError: cannot declare variable with name int.
```

Functions are checked for their return types. If a function
has return type `void`, a return statement is not required.

### code generation (SSA)

```sh
$ python3 -m gone.ircode Tests/mandel.g
================================================================================
FUNCTION: in_mandelbrot
	 ('MOVF', 0.0, 'R12')
	 ('ALLOCF', 'x')
	 ('STOREF', 'R12', 'x')
	 ('MOVF', 0.0, 'R13')
# ...
```

In this stage, the compiler does a depth-first walk of the syntax tree
and generates instructions in static single assignment form (SSA),
represented as a stream of tuples.

Every function contains a list of SSA instructions.
Global declarations are moved into an `__init` function,
which is called before the `main` functions is executed.
The `main` method is the entry point of the program.

The code generator will first evoke type checking on the input code.
If any type error is found, no instructions will be generated.

### code generation (LLVM IR)

```asm
$ python3 -m gone.llvmgen Tests/mandel.g
define i32 @"in_mandelbrot"(double %".1", double %".2", i32 %".3")
{
entry:
  %"x0" = alloca double
  store double %".1", double* %"x0"
  %"y0" = alloca double
  store double %".2", double* %"y0"
  %"n" = alloca i32
; ...
```

The `llvmgen` module takes the stream of SSA instructions
generated from the previous step,
and converts them into LLVM IR code,
so that they could be interpreted by Clang.
This step outputs similar code as Clang would,
when it transpiles C source code into LLVM IR:

```sh
clang -S foo.c -emit-llvm
```

Note that no static optimization is done at this stage;
all optimizations are done by LLVM itself.

At this point, a compiler frontend for the language "gone" is complete.
We can feed the output into Clang, with some bootstrapping code written in C:

```sh
python3 -m gone.compile Tests/mandel.g
./a.out
```

## Supported syntax

* numeric literals:

    * integers (`1234`, `0x1234`);
    * floats (`1.23`, `.123`, `123.`, `1.23e-1`);

* character literals (`a`, `\n`, `\x3f`, `\\`);

* boolean literals (`true`, `false`);

* type annotations (`int`, `float`, `char`, `bool`, `void`);

* operators:

    * arithmetic operators (`+`, `-`, `*`, `/`);
    * boolean operators (`<`, `>`, `==`, `!=`, `&&`, `||`, `!`);
    * augmented assignments (`+=`, `-=`);
    * increment and decrement (`++`, `--`);

* conditional statements (`if`, `else`, `while`, `for`);

    * `break` and `continue` statements;

* function definitions (`func`, `return`).

