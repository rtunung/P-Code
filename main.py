import argparse
from openai import OpenAI

from tools import all_tools, handle_tools

client = OpenAI(
    api_key="placeholder",
    base_url="http://localhost:5001/v1/"
)

def call_api(messages):
    completion = client.chat.completions.create(
        model="any",
        messages = messages,
        tools=all_tools
    )
    return completion

def agent_loop(initial_messages):
    messages = initial_messages.copy()

    while True:
        completion = call_api(messages)
        messages.append(completion.choices[0].message)

        if len(completion.choices[0].message.tool_calls) == 0:
            print(completion.choices[0].message.content)
            break

        tool_results = handle_tools(completion)
        messages.extend(tool_results)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()


    initial_messages =[
        {"role": "developer", "content": "You're a helpful AI agent for coding and other general tasks."},
        {
            "role": "user",
            "content": args.p
        }
    ]

    agent_loop(initial_messages)

if __name__ == "__main__":
    main()
