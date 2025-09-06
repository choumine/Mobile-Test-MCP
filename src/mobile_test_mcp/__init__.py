# __init__.py
from .common import app
from . import tool_get_ui_dump, tool_tap, tool_screenshot, tool_mark, tool_generate_report, tool_open_report, tool_execute_test
import os
from datetime import datetime



def main():
    # Get current date in YYYYMMDD format
    today_date = datetime.now().strftime("%Y%m%d")

    # Get current working directory
    current_dir = os.getcwd()

    # Combine to form the complete path for the new folder
    folder_path = os.path.join(current_dir, today_date)

    # Check if the folder exists, create it if it doesn't
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")

    # Set the current working directory to the new date folder
    os.chdir(folder_path)

    # Verify the working directory was set successfully
    print(f"Current working directory has been set to: {os.getcwd()}")

    app.run(transport='stdio')

if __name__ == "__main__":
    main()
