from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression:
            A mathematical expression like:
            123 * 456

    Returns:
        Calculation result.
    """

    try:
        result = eval(expression)
        return str(result)

    except Exception as e:
        return f"Error: {e}"