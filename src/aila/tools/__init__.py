from .calculator import calculator
from .knowledge_search import knowledge_search
from .learning_tools import get_learning_status, update_learning_status
from .memory_tools import get_learning_memory, update_learning_memory
from .web_search import web_search


TOOLS = [
    calculator,
    knowledge_search,
    web_search,
    get_learning_memory,
    update_learning_memory,
    get_learning_status,
    update_learning_status,
]
