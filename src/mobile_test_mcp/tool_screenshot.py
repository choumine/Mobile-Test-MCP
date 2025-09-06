from .common import app
import subprocess
import datetime
import os

@app.tool()
async def tool_screenshot() -> str:
    """
    Capture the current interface of an Android device via ADB and save to local directory
    
    Execution steps:
    1. Use adb shell screencap command to capture the screen
    2. Save the screenshot to /sdcard/screenshot.png on the device
    3. Use adb pull command to transfer the screenshot to local
    4. Name the local file with current date and time
    
    Returns:
        str: Path of the saved filename
    """
    try:
        # Generate filename based on current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        local_filename = f"screenshot_{timestamp}.png"
        
        # Capture screenshot on device and save to /sdcard/screenshot.png
        capture_command = ["adb", "shell", "screencap", "-p", "/sdcard/screenshot.png"]
        capture_result = subprocess.run(capture_command, capture_output=True, text=True)
        
        if capture_result.returncode != 0:
            raise Exception(f"Screenshot capture failed: {capture_result.stderr}")
        
        # Use adb pull to transfer screenshot to local
        pull_command = ["adb", "pull", "/sdcard/screenshot.png", local_filename]
        pull_result = subprocess.run(pull_command, capture_output=True, text=True)
        
        if pull_result.returncode != 0:
            raise Exception(f"Pulling screenshot failed: {pull_result.stderr}")
        
        return local_filename
    except Exception as e:
        raise Exception(f"Screenshot tool execution error: {str(e)}")