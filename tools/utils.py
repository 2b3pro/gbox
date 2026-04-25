import ast
import math
import sqlite3
import os
from .fs import _clean_path

_CALC_FUNCS = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow,
    **{k: getattr(math, k) for k in (
        "sqrt", "log", "log2", "log10", "exp",
        "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
        "floor", "ceil", "trunc", "factorial", "gcd",
    )},
}
_CALC_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau, "inf": math.inf, "nan": math.nan}
_CALC_BINOPS = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}
_CALC_UNARY = {ast.USub: lambda a: -a, ast.UAdd: lambda a: +a}

def _calc_walk(node):
    if isinstance(node, ast.Expression):
        return _calc_walk(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"unsupported literal: {type(node.value).__name__}")
    if isinstance(node, ast.Name):
        if node.id in _CALC_CONSTS:
            return _CALC_CONSTS[node.id]
        raise ValueError(f"unknown name: {node.id}")
    if isinstance(node, ast.BinOp):
        op = _CALC_BINOPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        return op(_calc_walk(node.left), _calc_walk(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _CALC_UNARY.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported unary: {type(node.op).__name__}")
        return op(_calc_walk(node.operand))
    if isinstance(node, ast.Call):
        if not (isinstance(node.func, ast.Name) and node.func.id in _CALC_FUNCS):
            raise ValueError("only whitelisted function calls allowed")
        args = [_calc_walk(a) for a in node.args]
        return _CALC_FUNCS[node.func.id](*args)
    raise ValueError(f"disallowed expression element: {type(node).__name__}")

def calculator(expression: str) -> str:
    """Evaluates an arithmetic expression. Supports math functions (sqrt, log, sin, ...)."""
    expr = _clean_path(expression)
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_calc_walk(tree))
    except SyntaxError as e:
        return f"Error: syntax: {e}"
    except Exception as e:
        return f"Error: {e}"

def sqlite_query(db_path: str, query: str) -> str:
    """Executes a READ-ONLY SQL query on a local SQLite database.
    
    Args:
        db_path: Path to the .sqlite or .db file.
        query: The SQL SELECT statement.
    """
    path = os.path.expanduser(_clean_path(db_path))
    if not os.path.exists(path):
        return f"Error: DB not found: {path}"
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [d[0] for d in cursor.description]
        conn.close()
        
        if not rows:
            return "No results."
        
        res = [", ".join(colnames)]
        for row in rows[:50]:
            res.append(", ".join(map(str, row)))
        return "\n".join(res)
    except Exception as e:
        return f"Error: {e}"

tools = [calculator, sqlite_query]
