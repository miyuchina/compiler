# Compiler

This repository implements a compiler for a subset of the Go programming language ("gone").

# Usage

This compiler requires Python 3.6 or above.
To use the compiler, the following packages are required:

* A working version of Clang;
* The latest version of [Anaconda](https://www.anaconda.com) Python;
* The latest version of [llvmlite](http://llvmlite.pydata.org/en/latest/) included with Anaconda;
* The latest version of [SLY](https://github.com/dabeaz/sly), a Python parser-generator.

To verify the compiler is working, clone the repo and run:

```sh
(cd gone && make)   # spawns a subshell
python3 -m gone.compile Tests/mandel.g
./a.out
```

This should reate an executable `a.out` in your working directory,
and plot a Mandelbrot set on your terminal screen.

The "gone" programming language generally follows Go's syntax.
To view `Tests/mandel.g` in vim, for example, running

```vimscript
set filetype=go
```

... should give you pretty good syntax highlighting.


