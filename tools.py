import json
import subprocess
import os

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


all_tools = [read_tool, log_tool, listdir_tool, file_tool]
