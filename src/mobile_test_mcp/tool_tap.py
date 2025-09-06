from .common import app

import subprocess
import sys

def execute_adb_tap(x, y):
    """
    Execute adb shell input tap command
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
    
    Returns:
        str: Execution result
    """
    try:
        # Build adb command
        command = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
        
        # Execute command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return f"Successfully executed tap operation: ({x}, {y})"
        else:
            return f"Execution failed: {result.stderr}"
            
    except FileNotFoundError:
        return "Error: adb command not found, please ensure adb is installed and added to system PATH"
    except Exception as e:
        return f"Execution error: {e}"


@app.tool()
def tool_tap(x, y):
    """
    This tool executes the tap function.
    
    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        str: Execution result
    """
    return execute_adb_tap(x, y)