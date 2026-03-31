Desktop Client Setup Guide
📋 Prerequisites
Python: Version 3.10 or higher.

🛠️ Installation
To set up the project on a new machine, the best approach is to install the project locally so all dependencies are handled automatically.

1. Navigate to the project directory:

Bash
cd "...\client websocket\desktop"
2. Update pip and install the project:

Bash
python -m pip install -U pip
pip install .
⚙️ Configuration
You must configure your environment variables before running the application. No code changes are required for this step.

Copy the desktop/.env file from your main machine to the new computer (or create a new .env file in the project directory) with at least the following variable:

Code snippet
WORKSPACE_ID=your_workspace_id_here
Optional Configurations:
If you need to point to a specific websocket URL directly, you can also add:

Code snippet
ASKUI_WS_URL=your_custom_ws_url_here
🚀 Running the Application
Once the installation and configuration are complete, you can start the desktop client by running:

Bash
askui-desktop
(Alternatively, you can run: python -m askui_desktop)

⚠️ Important Limitations
Hardcoded Ngrok URL: Currently, the code has a hardcoded BACKEND_BASE_URL (an ngrok URL) located in desktop/src/askui_desktop/config.py.

Action Required: The application will only work if that specific ngrok URL is still valid, active, and reachable from the new PC. If the ngrok session expires or the URL changes, you will need to update it. (Tip: In the future, it is highly recommended to modify the project to read this URL from the .env file instead of hardcoding it).
