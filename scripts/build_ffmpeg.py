"""
Script for verifying FFmpeg installation and downloading source code.
"""

import os
import sys
import subprocess
import platform
import logging
import requests
import tarfile
import re
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class FFmpegVerifier:
    def __init__(self, source_dir: str = "ffmpeg_src"):
        """
        Initialize the FFmpeg verifier.
        
        Args:
            source_dir: Directory to store FFmpeg source code
        """
        self.source_dir = Path(source_dir)
        self.system = platform.system().lower()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging for the verifier."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def get_ffmpeg_version(self) -> Optional[str]:
        """
        Get the installed FFmpeg version.
        
        Returns:
            FFmpeg version string or None if not found
        """
        try:
            # Try to get version using ffmpeg -version
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse version from output
            for line in result.stdout.splitlines():
                pattern = r"ffmpeg version (\d+(\.\d+)*)"
                match = re.search(pattern, line)
                if match:
                    version = match.group(1)
                    logger.info(f"Found FFmpeg version: {version}")
                    return version
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting FFmpeg version: {e.stderr}")
        except FileNotFoundError:
            logger.error("FFmpeg not found in system PATH")
        
        return None

    def download_source_code(self, version: str) -> Tuple[bool, Optional[Path]]:
        """
        Download FFmpeg source code for the given version.
        
        Args:
            version: FFmpeg version to download
            
        Returns:
            Tuple of (success, source_path)
        """
        try:
            # Create source directory if it doesn't exist
            self.source_dir.mkdir(parents=True, exist_ok=True)
            
            # Download URL
            url = f"https://www.ffmpeg.org/releases/ffmpeg-{version}.tar.bz2"
            archive_path = self.source_dir / f"ffmpeg-{version}.tar.bz2"
            
            # Download archive
            logger.info(f"Downloading FFmpeg source code from {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(archive_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract archive
            logger.info("Extracting source code...")
            with tarfile.open(archive_path, 'r:bz2') as tar:
                # Get the root directory name from the archive
                root_dir = tar.getmembers()[0].name.split('/')[0]
                
                # Extract all files
                for member in tar.getmembers():
                    # Skip the root directory itself
                    if member.name == root_dir:
                        continue
                    
                    # Remove the root directory prefix from the path
                    member.name = member.name[len(root_dir) + 1:]
                    
                    # Extract the file
                    tar.extract(member, path=self.source_dir)
            
            # Clean up archive
            archive_path.unlink()
            
            logger.info("Source code downloaded and extracted successfully")
            return True, self.source_dir
            
        except requests.RequestException as e:
            logger.error(f"Error downloading source code: {str(e)}")
        except tarfile.TarError as e:
            logger.error(f"Error extracting archive: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        
        return False, None

    def verify(self) -> bool:
        """
        Verify FFmpeg installation and download source code.
        
        Returns:
            True if verification successful, False otherwise
        """
        version = self.get_ffmpeg_version()
        if not version:
            logger.error("FFmpeg verification failed")
            return False
        
        success, _ = self.download_source_code(version)
        return success

def verify_ffmpeg() -> None:
    """Hook function called during package installation."""
    verifier = FFmpegVerifier()
    if not verifier.verify():
        sys.exit(1)

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        verify_ffmpeg()
    def finalize(self, version, build_data, artifact):
        # 可选：构建完成后的清理逻辑
        pass

if __name__ == "__main__":
    verify_ffmpeg() 