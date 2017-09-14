# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import ast

from typing import Callable

from yuuno.yuuno import Yuuno


def execute_code(expr, file):
    ipy = Yuuno.instance().environment.ipython
    expr = ipy.input_transformer_manager.transform_cell(expr)
    expr_ast = ipy.compile.ast_parse(expr)
    expr_ast = ipy.transform_ast(expr_ast)

    code = ipy.compile(ast.Expression(expr_ast.body[0].value), file, 'eval')
    return eval(code, ipy.user_ns, {})


class fake_dict(object):
    """
    Decorator for functions so that they behave like a dict
    """

    def __init__(self, func: Callable[[object], object]) -> None:
        self.func = func

    def __getitem__(self, it: object) -> object:
        return self.func(it)

