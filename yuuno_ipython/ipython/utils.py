# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
import time
import hashlib
import linecache

from typing import Callable

from yuuno.yuuno import Yuuno


EXECUTE_CODE_LINENO = 0
RESULT_VAR = '_yuuno_exec_last_'


def _code_name(code, file, number=0):
    hash_digest = hashlib.sha1(code.encode("utf-8")).hexdigest()
    return f"<{file}-{number}-{hash_digest[:12]}>"


def compile_with_cache(ipython, code, ast, file, symbol):
    # Increment the cache name.
    global EXECUTE_CODE_LINENO
    exec_no = EXECUTE_CODE_LINENO
    EXECUTE_CODE_LINENO += 1

    # Directly drop the fake python file into the cache.
    name = _code_name(code, file, exec_no)
    entry = (len(code), time.time(), [line + '\n' for line in code.splitlines()], name)
    linecache.cache[name] = entry
    if hasattr(linecache, '_ipython_cache'):
        linecache._ipython_cache[name] = entry

    # Compile the code
    return ipython.compile(ast, name, symbol)


def execute_code(expr, file, fail_on_error=True, ns=None):
    ipy = Yuuno.instance().environment.ipython
    expr = ipy.input_transformer_manager.transform_cell(expr)
    expr_ast = ipy.compile.ast_parse(expr)
    expr_ast = ipy.transform_ast(expr_ast)


    if len(expr_ast.body) == 0:
        # There is no code to execute.
        # Take the fast path and skip executing.
        return None

    elif isinstance(expr_ast.body[-1], ast.Expr):
        last_expr = expr_ast.body[-1]
        assign = ast.Assign(                                # _yuuno_exec_last_ = <LAST_EXPR>
            targets=[ast.Name(
                id=RESULT_VAR,
                ctx=ast.Store()
            )],
            value=last_expr.value
        )
        expr_ast.body[-1] = assign
    else:
        assign = ast.Assign(                                # _yuuno_exec_last_ = None
            targets=[ast.Name(
                id=RESULT_VAR,
                ctx=ast.Store(),
            )],
            value=ast.NameConstant(
                value=None
            )
        )
        expr_ast.body.append(assign)
    ast.fix_missing_locations(expr_ast)

    code = compile_with_cache(ipy, expr, expr_ast, file, "exec")

    if ns is None:
        ns = ipy.user_ns

    try:
        exec(code, ipy.user_ns, ns)
        result = ipy.user_ns.get(RESULT_VAR, None)
    finally:
        ns.pop(RESULT_VAR, None)
    return result
