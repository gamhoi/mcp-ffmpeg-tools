"""
MCP server interface for FFmpeg command execution.
Handles communication with LLMs and command processing.
"""

import json
import logging
import sys
import os
import io
# import asyncio
import subprocess
from pathlib import Path
# from urllib.parse import quote, unquote
from typing import Dict, Any, Optional, Annotated
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts.base import Message

ffmpeg_src_root = str(Path(__file__).resolve().parent.parent) + "/ffmpeg_src/"
# Create a server instance
mcp = FastMCP("ffmpeg-tools")

def execute_ff(args: list[str]) -> dict:
    """
    Execute an FFmpeg command using local file inputs/outputs.
    """
    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr
        }
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }

@mcp.tool("execute_ffmpeg", 
          description = "Full list of ffmpeg command arguments. Example: ['ffmpeg', '-i', 'in.mp4', 'out.mp4']")
def execute_ffmpeg(args: list[str]) -> dict:
    """
    Execute an ffmpeg command using local file inputs/outputs.
    """
    args += ["-v", "warning", "-y"]

    return execute_ff(args)

@mcp.tool("execute_ffprobe", 
          description = "Full list of ffprobe command arguments. Example: ['ffprobe', 'in.mp4']")
def execute_ffprobe(args: list[str]) -> dict:
    """
    Execute an ffprobe command using local file inputs/outputs.
    Network protocols like http/rtmp are not supported.
    """
    return execute_ff(args)

# @mcp.resource("ffmpeg-source://{path}",
#               name = "get_ffmpeg_source_code",
#               description =
# '''
# Read source code from a specified URI path, converting '/' to '%2F'. \
# Returns file contents or an error message. Example: ffmpeg-source://libavfilter%2Fsrc_movie.c
# '''
# )
@mcp.tool("get_ffmpeg_source_code",
          description = "Returns file contents or an error message. Example: /libavfilter/src_movie.c")
def get_ffmpeg_source_code(path: str) -> str:
    """
    Read source code from a specified path
    """
    if not path:
        raise ValueError("Missing file path")
    
    full_path = ffmpeg_src_root + path
    if not os.path.isfile(full_path):
        return f"Invalid path: {full_path}"

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
@mcp.tool("ls_ffmpeg_source_code",
          description = "Returns files or an error message. Example: /libavfilter/")
def ls_ffmpeg_source_code(path: str) -> list[str]:
    """
    list all of files in a specified path
    """
    if not path:
        raise ValueError("Missing file path")
    
    files = []
    try:
        for entry in Path(ffmpeg_src_root + path).glob('*'):
            files.append(entry.name)
        
        return files
    except Exception as e:
        raise RuntimeError(f"Error reading file: {str(e)}")

@mcp.tool("get_screenshot", description="Get a screenshot from a media file at a given timestamp. Parameters: file path and timestamp (format '00:00:00'). Return an Image object.")
def get_screenshot(file_path: str, timestamp: str) -> Image:
    """
    Extract a screenshot from a media file at the specified timestamp and return as an Image.
    """
    # Build ffmpeg command to output PNG to stdout
    cmd = [
        "ffmpeg",
        "-ss", timestamp,  # seek to timestamp
        "-i", file_path,
        "-frames:v", "1",  # extract one frame
        "-f", "image2pipe",
        "-vcodec", "png",
        "-v", "error",
        "-y",
        "-"
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        if proc.returncode != 0 or not proc.stdout:
            raise RuntimeError(f"ffmpeg error: {proc.stderr}")
        # Return as Image (in-memory bytes)
        return Image(data=proc.stdout, format="png")
    except Exception as e:
        raise RuntimeError(f"Failed to extract screenshot: {e}")

def main():
    """
    Run the MCP server.
    """
    mcp.run()

if __name__ == "__main__":
    main()
