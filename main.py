import argparse
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

from tools import ALL_TOOLS, handle_tools, set_bash_timeout
from utils import count_tokens

rich_console = Console()

developer_prompt = {"role": "developer", "content": "You're a helpful AI agent for coding and other general tasks. Think through the problems step-by-step. Use the Log tool to keep the user updated and to explain your reasoning for tool usage. Be careful with the Bash tool, it can be used to interact with system and even the internet via curl."}

MESSAGE_PRUNING_ENABLED = True
ALLOWED_TOKENS = 40000

def get_completion(client:OpenAI, messages, model_name):
    completion = client.chat.completions.create(
        model=model_name,
        messages = messages,
        tools=ALL_TOOLS
    )
    return completion

def prune_messages(messages, current_tokens:int, allowed_tokens:int, model_name:str):

    def get_latest_user_prompt_pos():
        for i in range(len(messages) -1, 0):
            if isinstance(messages[i], dict) and messages[i]["role"] == "user":
                return i
        return 1

    def get_token_count(message):
        content = ""
        if hasattr(message, "content") and message.content:
            content = message.content
        elif isinstance(message, dict) and "content" in message:
            content = message["content"]

        return count_tokens(content, model_name)

    def check_if_tool(message):
        return isinstance(message, dict) and message["role"] == "tool"

    current_token_estimate = current_tokens
    print(f"SYSTEM: Current tokens: {current_token_estimate}")
    latest_user_pos = get_latest_user_prompt_pos()
    while current_token_estimate > allowed_tokens or (len (messages) >= 2 and check_if_tool(messages[1])):
        removed_message = None
        if latest_user_pos == 1:
            removed_message = messages.pop(2)
        else:
            removed_message = messages.pop(1)
            latest_user_pos -= 1

        current_token_estimate -= get_token_count(removed_message)
        print("SYSTEM: Pruned one message")
        print(f"SYSTEM: Current tokens: {current_token_estimate}")


def agent_loop(client:OpenAI, messages, model_name):

    while True:
        completion = get_completion(client, messages, model_name)

        # Update model name if the API returns a specific one (e.g. if 'any' was used)
        # Note: This depends on the API provider returning the actual model used in the response
        actual_model = completion.model if hasattr(completion, 'model') and model_name == "any" else model_name

        messages.append(completion.choices[0].message)

        prune_messages(messages=messages, current_tokens=completion.usage.total_tokens, allowed_tokens=ALLOWED_TOKENS, model_name=actual_model)

        if len(completion.choices[0].message.tool_calls) == 0:
            markdown = Markdown(f"**Agent:** {completion.choices[0].message.content}")
            rich_console.print(markdown)
            break

        tool_results = handle_tools(completion)
        messages.extend(tool_results)

def single_call(client, content, model_name):
    initial_messages = [developer_prompt, {"role": "user", "content": content}]
    agent_loop(client, initial_messages, model_name)

def interactive_mode(client, model_name):
    print("Welcome to the interactive mode")
    messages = [developer_prompt]

    while True:
        prompt = input("> ")
        if prompt == "/exit":
            break

        messages.append({"role": "user", "content": prompt})
        agent_loop(client, messages, model_name)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=False, help="Run a single given prompt", type=str)
    p.add_argument("-u", required=False, help="Set the base url for OpenAI api", type=str)
    p.add_argument("-k", required=False, help="Set the api key for the OpenAI api", type=str)
    p.add_argument("-m", "--model", required=False, help="Set the model name", type=str, default="any")
    p.add_argument("--bash-timeout", required=False, help="Set the timeout for Bash tool calls", type=float)
    p.add_argument("--max-allowed-context", required=False, help="Set the size of the allowed context window", type=int)
    args = p.parse_args()

    api_key = "placeholder"
    base_url = "http://localhost:5001/v1/"

    if args.u:
        base_url = args.u

    if args.k:
        api_key = args.k

    if args.bash_timeout:
        set_bash_timeout(args.bash_timeout)

    if args.max_allowed_context:
        global ALLOWED_TOKENS
        ALLOWED_TOKENS = args.max_allowed_context

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    print("Starting agent...")
    print(f"Connecting to {client._base_url}")

    if args.p:
        single_call(client, args.p, args.model)
        return

    interactive_mode(client, args.model)

if __name__ == "__main__":
    main()
