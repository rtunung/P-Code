import os
import json
import subprocess
import argparse
from openai import OpenAI

client = OpenAI(
    api_key="placeholder",
    base_url="http://localhost:5001/v1/"
)


read_tool = {
    "type": "function",
    "function": {
    "name": "Read",
    "description": "Read and return the contents of a file",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "The path to the file to read"
        }
      },
      "required": ["file_path"]
    }
  }
}

log_tool = {
    "type": "function",
    "function": {
    "name": "Log",
    "description": "Inform the user about current happenings and activities",
    "parameters": {
      "type": "object",
      "properties": {
        "log_message": {
          "type": "string",
          "description": "The message to be logged"
        }
      },
      "required": ["log_message"]
    }
  }
}


listdir_tool = {
    "type": "function",
    "function": {
    "name": "ListDir",
    "description": "List all files in the given directory",
    "parameters": {
      "type": "object",
      "properties": {
        "directory": {
          "type": "string",
          "description": "The directory to have it's files displayed"
        }
        },
        "required": ["directory"]
    }
  }
}

file_tool = {
    "type": "function",
    "function": {
    "name": "FileInfo",
    "description": "Get information about the file type",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "Path to the file to be checked"
        }
        },
        "required": ["file_path"]
    }
  }
}

def handle_tool_file(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or len(args) == 0:
        raise RuntimeError("No arguments provided")
    result = subprocess.run(['file', args['file_path']], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def handle_tool_listdir(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or len(args) == 0:
        raise RuntimeError("No arguments provided")
    return json.dumps(os.listdir(args["directory"]))

def handle_tool_log(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or len(args) == 0:
        raise RuntimeError("No arguments provided")
        
    print(f"LOG: {args["log_message"]}")
    return "Ok"

def handle_tool_read(tcall):
    if tcall.function.name != "Read":
        raise RuntimeError("Not a read tool call. This should not happen.")

    args = json.loads(tcall.function.arguments)
    if not args or len(args) == 0:
        raise RuntimeError("No arguments provided")

    file = open(args["file_path"], "r")

    content = file.read()
    file.close()
    return content
        
def handle_tools(completion):
    results = []
    for tcall in completion.choices[0].message.tool_calls:
        result = None
        if tcall.function.name == "Read":
            result = handle_tool_read(tcall)
        elif tcall.function.name == "Log":
            result = handle_tool_log(tcall)
        elif tcall.function.name == "ListDir":
            result = handle_tool_listdir(tcall)
        elif tcall.function.name == "FileInfo":
            result = handle_tool_file(tcall)

        if result != None:
            results.append({"role": "tool", "tool_call_id": tcall.id, "content": result})

    return results

def call_api(messages):
    completion = client.chat.completions.create(
        model="any",
        messages = messages,
        tools=[read_tool, log_tool, listdir_tool, file_tool]
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
