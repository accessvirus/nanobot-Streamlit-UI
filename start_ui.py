import subprocess
import sys
import os

os.chdir(r"H:\Users\m.2 SSD\Desktop\coding\GenUI\codestorm\nanobot")

print("Starting Nanobot Streamlit UI...")
print("Server will be available at: http://localhost:8858")
print("Press Ctrl+C to stop\n")

subprocess.run([
    sys.executable, "-m", "streamlit", "run", 
    "streamlit_app/app.py",
    "--server.port", "8858",
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--browser.gatherUsageStats", "false"
])