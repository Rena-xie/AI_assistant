"""Command line entry point of the AI Learning Assistant.

Call chain::

    main.py  ->  runtime/runner.py  ->  agent.py  ->  ChatOpenAI

`main.py` only owns the interactive input loop. The model is never called
directly here; every user message goes through `run_agent()`.
"""

from .agent import create_agent
from .runtime.runner import run_agent


def main():
    """Run the chat loop until the user types ``exit``.

    The message is passed to `run_agent()`, which owns the model call.
    """

    agent = create_agent()

    while True:

        user_input = input("\nUser: ")

        if user_input == "exit":
            break

        response = run_agent(
            agent,
            user_input
        )

        print(
            "\nAssistant:",
            response.content
        )


if __name__ == "__main__":
    main()