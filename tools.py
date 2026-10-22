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

write_tool = {
    "type": "function",
    "function": {
    "name": "Write",
    "description": "Write content to file after user approval",
    "parameters": {
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
    if not args or not ("file_path" in args):
        return ("Error", "Missing argument 'file_path'")

    result = subprocess.run(['file', args['file_path']], stdout=subprocess.PIPE)
    return ("Success", result.stdout.decode('utf-8'))

def handle_tool_listdir(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or not ("directory" in args):
        return ("Error", "Missing argument 'directory'")

    return ("Success", json.dumps(os.listdir(args["directory"])))

def handle_tool_log(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or not ("log_message" in args):
        return ("Error", "Missing argument 'log_message'")

    print(f"LOG: {args["log_message"]}")
    return ("Success", "")

def handle_tool_read(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or not ("file_path" in args):
        return ("Error", "Missing argument 'file_path'")

    file = None
    try:
        file = open(args["file_path"], "r")
    except FileNotFoundError as e:
        return ("Error", e.strerror)

    content = file.read()
    file.close()
    return ("Success", content)

def handle_tool_write(tcall):
    args = json.loads(tcall.function.arguments)
    if not args or not ("file_path" in args) or not ("content" in args):
        return ("Error", "Missing required arguments 'file_path' or 'content'")

    print(f"Agent wants to write to file '{args["file_path"]}'")
    approval = input("Approve? (y/n): ")
    if approval.lower() != "y":
        return ("Error", f"User rejected writting to file '{args["file_path"]}'")

    file = None
    try:
        file = open(args["file_path"], "w")
    except FileNotFoundError as e:
        return ("Error", e.strerror)

    file.write(args["content"])
    file.close()
    return ("Success", f"Written contents to '{args["file_path"]}'")


def handle_tools(completion):
    results = []
    for tcall in completion.choices[0].message.tool_calls:
        result = None
        if tcall.function.name == "Read":
            result = handle_tool_read(tcall)
        elif tcall.function.name == "Write":
            result = handle_tool_write(tcall)
        elif tcall.function.name == "Log":
            result = handle_tool_log(tcall)
        elif tcall.function.name == "ListDir":
            result = handle_tool_listdir(tcall)
        elif tcall.function.name == "FileInfo":
            result = handle_tool_file(tcall)

        if result != None:
            (status, content) = result
            results.append({"role": "tool", "tool_call_id": tcall.id, "status": status, "content": content})

    return results


all_tools = [read_tool, log_tool, listdir_tool, file_tool, write_tool]
