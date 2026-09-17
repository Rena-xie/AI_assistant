def run_agent(agent, message):

    result = agent.invoke(
        {
            "messages":[
                {
                 "role":"user",
                 "content":message
                }
            ]
        }
    )

    return result