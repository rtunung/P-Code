import argparse
import logging
import sys
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

from tools import ALL_TOOLS, handle_tools, set_bash_timeout
from utils import count_tokens, logger

rich_console = Console()

developer_prompt = {"role": "developer", "content": "You're a helpful AI agent for coding and other general tasks. Think through the problems step-by-step. Use the Log tool to keep the user updated and to explain your reasoning for tool usage, keep those messages short. Be careful with the Bash tool, it can be used to interact with system and even the internet via curl."}

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
    logger.debug(f"Current token amount: {current_token_estimate}")
    latest_user_pos = get_latest_user_prompt_pos()
    pruned_num = 0
    while current_token_estimate > allowed_tokens or (len (messages) >= 2 and check_if_tool(messages[1])):
        removed_message = None
        if latest_user_pos == 1:
            removed_message = messages.pop(2)
        else:
            removed_message = messages.pop(1)
            latest_user_pos -= 1
        pruned_num += 1

        current_token_estimate -= get_token_count(removed_message)

    if pruned_num > 0:
        logger.debug(f"Pruned {pruned_num} message(s)")
        logger.debug(f"Current token amount: {current_token_estimate}")


def agent_loop(client:OpenAI, messages, model_name):

    while True:
        completion = get_completion(client, messages, model_name)

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
    parser = argparse.ArgumentParser(description="P-Code AI Agent for coding and general tasks")
    parser.add_argument("-p", "--prompt", help="run a single prompt", type=str)
    parser.add_argument("-u", "--url", help="set the base url for OpenAI api", type=str, default="http://localhost:5001/v1/")
    parser.add_argument("-k", "--key", help="set the api key for the OpenAI api", type=str, default="placeholder")
    parser.add_argument("-m", "--model", help="set the model name", type=str, default="any")
    parser.add_argument("-c","--max-allowed-context", help="set the size of the allowed context window", type=int, default=40000)
    parser.add_argument("--bash-timeout", help="set the timeout for Bash tool calls", type=float, default=30.0)
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.INFO)

    set_bash_timeout(args.bash_timeout)
    global ALLOWED_TOKENS
    ALLOWED_TOKENS = args.max_allowed_context

    client = OpenAI(
        api_key=args.key,
        base_url=args.url
    )

    print("Starting agent...")
    print(f"Connecting to {client._base_url}")

    if args.prompt:
        single_call(client, args.prompt, args.model)
        return

    interactive_mode(client, args.model)

if __name__ == "__main__":
    main()
