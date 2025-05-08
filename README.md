# mcp-ffmpeg-tools

An open-source Python MCP (Model-Command Protocol) server designed to enable Large Language Models (LLMs) to execute FFmpeg commands, receive execution results, and validate commands against FFmpeg source code.

## Prerequisites

Before installing mcp-ffmpeg-tools, you need to have FFmpeg installed on your system:

### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the archive to a location of your choice
3. Add the `bin` directory to your system PATH

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (Fedora)
```bash
sudo dnf install ffmpeg
```

## Features

- Execute FFmpeg commands through an MCP interface
- Receive detailed execution results and error messages
- Access FFmpeg source code for command correction
- Cross-platform support (Windows, macOS, Linux)
- Environment management using uv

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gamhoi/mcp-ffmpeg-tools.git
cd mcp-ffmpeg-tools
```

2. Install using uv:
```bash
uv venv
uv pip install -e .
```

The installation process will:
1. Verify that FFmpeg is installed and accessible in your system PATH
2. Download the corresponding FFmpeg source code for validation
3. Install the Python package and its dependencies

If FFmpeg is not found or the source code download fails, the installation will fail.

## Usage

### Usage with Claude Desktop

Add the following configuration to your Claude Desktop settings:

```json
{
    "mcpServers": {
        "mcp-ffmpeg-tools": {
            "command": "uv",
            "args": [
                "--directory",
                "PATH_TO/mcp-ffmpeg-tools",
                "run",
                "ffmpeg-tools"
            ]
        }
    }
}
```

### Running Tests

```bash
uv run python3 client/test.py
```

### Prompt Examples

#### Base prompt
```
Help me perform media conversion tasks using FFmpeg. You can:
- use tool:execute_ffmpeg to run FFmpeg commands
- use tool:execute_ffprobe to inspect results (e.g., resolution, bitrate)
- use tool:get_screenshot to inspect results (e.g., video layout, quality)
- use tool:ls_ffmpeg_source_code and tool:get_ffmpeg_source_code to validate commands using FFmpeg source code
```

#### Extract video and audio
```
Extract all media streams from the file 'YOU_FILE_PATH' and save outputs to 'YOU_OUTPUT_PATH'
```

#### Overlay 2 videos
```
Overlay file1 'YOU_FILE_PATH_1' and file2 'YOU_FILE_PATH_2', using file1 as the background. Scale file2 down to half its original resolution and position it at the top-right corner of file1. Save the output to 'YOUR_OUTPUT_PATH'.
```
