from agent import ToolAgent

if __name__ == "__main__":
    agent = ToolAgent()

    user_input = input("Введите задачу агенту: ")
    agent.add_user_message(user_input)

    result = agent.run()
    print("\nРезультат:\n", result)
