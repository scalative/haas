#!/bin/bash

if python --version 2>&1 | grep PyPy >/dev/null; then
    git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    pyenv install "pypy-${1}"
    pyenv global "pypy-${1}"
    pypy --version
fi
