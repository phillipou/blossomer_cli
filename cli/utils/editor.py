"""
Smart editor detection and integration utilities.
"""

import os
import subprocess
import shutil
from typing import Optional, List
from pathlib import Path


def detect_editor() -> str:
    """
    Detect the user's preferred editor using smart fallbacks.
    
    Returns:
        Editor command to use
    """
    # 1. Check EDITOR environment variable
    if os.environ.get('EDITOR'):
        editor = os.environ['EDITOR']
        if shutil.which(editor.split()[0]):  # Check if command exists
            return editor
    
    # 2. Check VISUAL environment variable  
    if os.environ.get('VISUAL'):
        visual = os.environ['VISUAL']
        if shutil.which(visual.split()[0]):
            return visual
    
    # 3. Try common editors in order of preference
    preferred_editors = [
        'code',     # VS Code
        'code-insiders',  # VS Code Insiders
        'subl',     # Sublime Text
        'atom',     # Atom
        'vim',      # Vim
        'vi',       # Vi
        'nano',     # Nano
        'emacs',    # Emacs
        'notepad',  # Windows Notepad (if on Windows)
    ]
    
    for editor in preferred_editors:
        if shutil.which(editor):
            return editor
    
    # 4. Platform-specific fallbacks
    import platform
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        return 'open -t'  # TextEdit
    elif system == 'Windows':
        return 'notepad'
    else:  # Linux/Unix
        return 'vi'  # Should always be available


def open_file_in_editor(file_path: Path, editor: Optional[str] = None) -> bool:
    """
    Open a file in the user's preferred editor.
    
    Args:
        file_path: Path to the file to edit
        editor: Specific editor to use (optional, will auto-detect if None)
        
    Returns:
        True if successful, False if failed
    """
    if editor is None:
        editor = detect_editor()
    
    try:
        # Handle special cases
        if editor == 'open -t':  # macOS TextEdit
            subprocess.run(['open', '-t', str(file_path)], check=True)
        elif 'code' in editor:  # VS Code variants
            subprocess.run([editor, str(file_path)], check=True)
        else:
            # Most editors can be called directly with the file path
            subprocess.run([editor, str(file_path)], check=True)
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error opening editor: {e}")
        return False


def get_editor_info() -> dict:
    """
    Get information about the detected editor.
    
    Returns:
        Dictionary with editor information
    """
    editor = detect_editor()
    
    # Try to get version info for common editors
    version = "unknown"
    try:
        if 'code' in editor:
            result = subprocess.run([editor, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
        elif editor == 'vim':
            result = subprocess.run(['vim', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
    except:
        pass  # Ignore version detection errors
    
    return {
        'command': editor,
        'name': _get_editor_name(editor),
        'version': version,
        'available': shutil.which(editor.split()[0]) is not None
    }


def _get_editor_name(command: str) -> str:
    """Get human-readable editor name from command."""
    name_map = {
        'code': 'Visual Studio Code',
        'code-insiders': 'Visual Studio Code (Insiders)', 
        'subl': 'Sublime Text',
        'atom': 'Atom',
        'vim': 'Vim',
        'vi': 'Vi',
        'nano': 'Nano',
        'emacs': 'Emacs',
        'notepad': 'Notepad',
        'open -t': 'TextEdit (macOS)'
    }
    
    return name_map.get(command, command)


# Test function
if __name__ == "__main__":
    print("Editor Detection Test:")
    print("=" * 30)
    
    info = get_editor_info()
    print(f"Detected Editor: {info['name']}")
    print(f"Command: {info['command']}")
    print(f"Available: {info['available']}")
    print(f"Version: {info['version']}")
    
    print(f"\nEnvironment Variables:")
    print(f"EDITOR: {os.environ.get('EDITOR', 'Not set')}")
    print(f"VISUAL: {os.environ.get('VISUAL', 'Not set')}")