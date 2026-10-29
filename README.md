# P-Code AI Agent

A simple terminal-based AI agent designed for coding and general automation tasks. This agent can interact with your local file system, execute shell commands, and perform complex reasoning to solve programming problems.

## Features

- **Tool-Calling Capabilities**: The agent can use several specialized tools:
  - `Read`: Read the contents of any file.
  - `Write`: Write new content to files (with user approval).
  - `ListDir`: List files and directories.
  - `FileInfo`: Get detailed file information.
  - `Bash`: Execute arbitrary shell commands (with user approval).
  - `Log`: Log activities and reasoning to the console.
- **Safety**: Critical operations like `Write` and `Bash` require explicit user confirmation before execution.
- **Smart Context Management**: Automatically prunes conversation history to stay within the model's token limit.
- **OpenAI API Backend**: Compatible with any OpenAI-compatible API (e.g., LocalAI, Ollama, vLLM).

## Disclaimer

**IMPORTANT: This agent does NOT track or report generated token costs.** 

This agent was primarily developed for use with **local models**. If you use this agent with a paid API provider, be aware that you are responsible for all costs incurred during usage.

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- A running OpenAI-compatible API server (e.g., LocalAI or Ollama)

### Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode
Start an interactive chat session:
```bash
python main.py -u <your-api-url> -k <your-api-key>
```

### Single Prompt Mode
Run a single prompt and exit:
```bash
python main.py -p "Summarize the contents of main.py" -u <your-api-url> -k <your-api-key>
```

### Configuration Options
| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--prompt` | `-p` | A single prompt to run | None |
| `--url` | `-u` | Base URL for OpenAI API | `http://localhost:5001/v1/` |
| `--key` | `-k` | API Key | `placeholder` |
| `--model` | `-m` | Model name | `any` |
| `--max-allowed-context` | `-c` | Max tokens allowed before messages are getting pruned | `40000` |
| `--bash-timeout` | | Timeout for Bash commands | `30.0` |
