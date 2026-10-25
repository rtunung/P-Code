import json
import subprocess
import os
from typing import Any
from utils import truncate_dictionary

TOOL_MAP = {}
ALL_TOOLS = []
LOG_TOOL_CALLS = True
BASH_TIMEOUT = 30.0

def make_tool(name:str, description:str, parameters:dict[str, Any]):
    def decorator(function):
        new_tool = {
            "type": "function",
            "function": {
            "name": name,
            "description": description,
            "parameters": parameters
          }
        }
        TOOL_MAP[name] = function
        ALL_TOOLS.append(new_tool)

        return function

    return decorator


@make_tool(
    name= "Read",
    description= "Read and return the contents of a file",
    parameters= {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The path to the file to read"
        }
      },
      "required": ["file_path"]
    }
)
def handle_tool_read(args):
    if not args or not ("file_path" in args):
        return ("Error", "Missing argument 'file_path'")

    try:
        with open(args["file_path"], "r") as file:
            content = file.read()
            return ("Success", content)
    except FileNotFoundError as e:
        return ("Error", e.strerror)


@make_tool(
    name="Write",
    description="Write content to file after user approval",
    parameters= {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The path to the file to be written"
        },
        "content": {
          "type": "string",
          "description": "The content to be written"
        }
      },
      "required": ["file_path"]
    }
)
def handle_tool_write(args):
    if not args or not ("file_path" in args) or not ("content" in args):
        return ("Error", "Missing required arguments 'file_path' or 'content'")

    print(f"Agent wants to write to file '{args["file_path"]}'")
    approval = input("Approve? (y/n): ")
    if approval.lower() != "y":
        return ("Error", f"User rejected writting to file '{args["file_path"]}'")

    try:
        with open(args["file_path"], "w") as file:
            file.write(args["content"])
            return ("Success", f"Written contents to '{args["file_path"]}'")
    except FileNotFoundError as e:
        return ("Error", e.strerror)


@make_tool(
    name="FileInfo",
    description="Get information about the file type",
    parameters= {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "Path to the file to be checked"
        }
        },
        "required": ["file_path"]
    }
)
def handle_tool_file(args):
    if not args or not ("file_path" in args):
        return ("Error", "Missing argument 'file_path'")

    result = subprocess.run(['file', args['file_path']], capture_output=True, text=True)
    return ("Success", result.stdout)


@make_tool(
    name="Log",
    description="Inform the user about current happenings and activities",
    parameters={
      "type": "object",
      "properties": {
        "log_message": {
          "type": "string",
          "description": "The message to be logged"
        }
      },
      "required": ["log_message"]
    }
)
def handle_tool_log(args):
    if not args or not ("log_message" in args):
        return ("Error", "Missing argument 'log_message'")

    print(f"LOG: {args["log_message"]}")
    return ("Success", "")


@make_tool(
    name="ListDir",
    description="List all files in the given directory",
    parameters={
      "type": "object",
      "properties": {
        "directory": {
          "type": "string",
          "description": "The directory to have it's files displayed"
        }
        },
        "required": ["directory"]
    }
)
def handle_tool_listdir(args):
    if not args or not ("directory" in args):
        return ("Error", "Missing argument 'directory'")

    return ("Success", json.dumps(os.listdir(args["directory"])))


@make_tool(
    name="Bash",
    description="Execute a shell command after user approval",
    parameters= {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "description": "The command to execute"
        }
      },
    "required": ["command"],
    }
)
def handle_tool_bash(args):
    if not args or not ("command" in args):
        return ("Error", "Missing argument 'command'")

    print(f"Agent wants to execute the command '{args["command"]}'")
    approval = input("Approve? (y/n): ")
    if approval.lower() != "y":
        return ("Error", f"User rejected to execute the command '{args["command"]}'")

    try:
        result = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=BASH_TIMEOUT)
        if result.stdout:
            return ("Success", result.stdout)
        else:
            return ("Error", result.stderr)
    except subprocess.TimeoutExpired as timeout:
        return ("Error", f"Command timed out after {BASH_TIMEOUT} seconds")


def handle_tools(completion):
    results = []
    for tcall in completion.choices[0].message.tool_calls:
        name = tcall.function.name
        args = json.loads(tcall.function.arguments)

        handler = TOOL_MAP.get(name)
        if handler:
            if(LOG_TOOL_CALLS) and name != "Log":
                print(f"SYSTEM LOG: Agent made tool call {name}({truncate_dictionary(args)})")
            (status, content) = handler(args)
            results.append({"role": "tool", "tool_call_id": tcall.id, "content": f"Status: {status}, Content:{content}"})

    return results

def set_bash_timeout(timeout:float):
    global BASH_TIMEOUT
    BASH_TIMEOUT = timeout
