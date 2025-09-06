from .common import app
import subprocess
import os
import platform


@app.tool()
async def tool_open_report(file_path: str) -> str:
    """
    Open the HTML report file at the specified path
    
    Parameters:
        file_path (str): Path to the HTML report file
        
    Returns:
        str: Execution result information
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist"
        
        # Check if file is an HTML file
        if not file_path.endswith('.html'):
            return f"Error: File {file_path} is not an HTML file"
        
        # Choose opening method based on operating system
        system = platform.system()
        
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", file_path])
        else:
            # Try to open using webbrowser module
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
            
        return f"Successfully opened report file: {file_path}"
        
    except Exception as e:
        return f"Error opening file: {str(e)}"