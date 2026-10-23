import argparse
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

from tools import all_tools, handle_tools

client = OpenAI(
    api_key="placeholder",
    base_url="http://localhost:5001/v1/"
)

rich_console = Console()

developer_prompt = {"role": "developer", "content": "You're a helpful AI agent for coding and other general tasks. Think through the problems step-by-step. Use the Log tool to keep the user updated and to explain your reasoning for tool usage."}

def call_api(messages):
    completion = client.chat.completions.create(
        model="any",
        messages = messages,
        tools=all_tools
    )
    return completion

def agent_loop(messages):

    while True:
        completion = call_api(messages)
        messages.append(completion.choices[0].message)

        if len(completion.choices[0].message.tool_calls) == 0:
            markdown = Markdown(f"**Agent:** {completion.choices[0].message.content}")
            rich_console.print(markdown)
            break

        tool_results = handle_tools(completion)
        messages.extend(tool_results)

def single_call(content):
    initial_messages = [developer_prompt, {"role": "user", "content": content}]
    agent_loop(initial_messages)

def interactive_mode():
    messages = [developer_prompt]

    while True:
        prompt = input("> ")
        if prompt == "/exit":
            break

        messages.append({"role": "user", "content": prompt})
        agent_loop(messages)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=False, help="run a single given prompt")
    args = p.parse_args()

    if args.p:
        single_call(args.p)
        return

    interactive_mode()

if __name__ == "__main__":
    main()
