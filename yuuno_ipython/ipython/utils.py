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
from IPython.core.interactiveshell import ExecutionResult

from typing import Callable

from yuuno.yuuno import Yuuno


RESULT_VAR = '_yuuno_exec_last_'


def execute_code(expr, file, fail_on_error=True):
    ipy = Yuuno.instance().environment.ipython
    expr = ipy.input_transformer_manager.transform_cell(expr)
    expr_ast = ipy.compile.ast_parse(expr)
    expr_ast = ipy.transform_ast(expr_ast)

    if isinstance(expr_ast.body[-1], ast.Expr):
        last_expr = expr_ast.body[-1]
        assign = ast.Assign(
            targets=[ast.Name(
                id=RESULT_VAR,
                ctx=ast.Store(),
                lineno=last_expr.lineno,
                col_offset=last_expr.col_offset
            )],
            value=last_expr.value
        )
        assign.lineno = last_expr.lineno
        assign.col_offset = last_expr.col_offset
        expr_ast.body[-1] = assign
        expr_ast.body.append(
            ast.Expr(
                value=ast.Name(
                    id=RESULT_VAR,
                    ctx=ast.Load(),
                    lineno=last_expr.lineno,
                    col_offset=last_expr.col_offset
                ),
                lineno=last_expr.lineno,
                col_offset=last_expr.col_offset
            )
        )

    _nothing = []
    before = ipy.user_ns.get(RESULT_VAR, _nothing)

    if ipy.run_ast_nodes(expr_ast.body, file, 'none'):
        if fail_on_error:
            raise RuntimeError("Failed to execute code.")
        return

    result = ipy.user_ns.pop(RESULT_VAR, None)
    if before is not _nothing:
        ipy.user_ns[RESULT_VAR] = before
    return result


class fake_dict(object):
    """
    Decorator for functions so that they behave like a dict
    """

    def __init__(self, func: Callable[[object], object]) -> None:
        self.func = func

    def __getitem__(self, it: object) -> object:
        return self.func(it)

