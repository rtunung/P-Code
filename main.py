import argparse
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

from tools import ALL_TOOLS, handle_tools

rich_console = Console()

developer_prompt = {"role": "developer", "content": "You're a helpful AI agent for coding and other general tasks. Think through the problems step-by-step. Use the Log tool to keep the user updated and to explain your reasoning for tool usage. Be careful with the Bash tool, it can be used to interact with system and even the internet via curl."}

def call_api(client, messages):
    completion = client.chat.completions.create(
        model="any",
        messages = messages,
        tools=ALL_TOOLS
    )
    return completion

def agent_loop(client, messages):

    while True:
        completion = call_api(client, messages)
        messages.append(completion.choices[0].message)

        if len(completion.choices[0].message.tool_calls) == 0:
            markdown = Markdown(f"**Agent:** {completion.choices[0].message.content}")
            rich_console.print(markdown)
            break

        tool_results = handle_tools(completion)
        messages.extend(tool_results)

def single_call(client, content):
    initial_messages = [developer_prompt, {"role": "user", "content": content}]
    agent_loop(client, initial_messages)

def interactive_mode(client):
    print("Welcome to the interactive mode")
    messages = [developer_prompt]

    while True:
        prompt = input("> ")
        if prompt == "/exit":
            break

        messages.append({"role": "user", "content": prompt})
        agent_loop(client, messages)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=False, help="Run a single given prompt")
    p.add_argument("-u", required=False, help="Set the base url for OpenAI api")
    p.add_argument("-k", required=False, help="Set the api key for the OpenAI api")
    args = p.parse_args()

    api_key = "placeholder"
    base_url = "http://localhost:5001/v1/"

    if args.u:
        base_url = args.u

    if args.k:
        api_key = args.k

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    print("Starting agent...")
    print(f"Connecting to {client._base_url}")

    if args.p:
        single_call(client, args.p)
        return

    interactive_mode(client)

if __name__ == "__main__":
    main()
