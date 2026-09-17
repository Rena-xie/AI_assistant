from .agent import create_agent


def main():

    agent = create_agent()

    while True:

        user_input = input("\nUser: ")

        if user_input == "exit":
            break

        response = agent.invoke(
            user_input
        )

        print(
            "\nAssistant:",
            response.content
        )


if __name__ == "__main__":
    main()