from langchain_core.tools import tool
import ast
import operator


operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


@tool
def calculator(expression: str) -> str:
    """
    Calculate a basic mathematical expression.

    Example:
        123 * 456

    Args:
        expression:
            Mathematical expression.

    Returns:
        Calculation result.
    """

    try:
        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = _evaluate(tree.body)

        return str(result)

    except Exception as e:
        return f"Error: {e}"


def _evaluate(node):

    if isinstance(node, ast.Constant):

        return node.value


    if isinstance(node, ast.BinOp):

        operator_func = operators[type(node.op)]

        return operator_func(
            _evaluate(node.left),
            _evaluate(node.right)
        )


    raise ValueError(
        "Unsupported expression"
    )