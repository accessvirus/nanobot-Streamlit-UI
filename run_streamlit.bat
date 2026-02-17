@echo off
echo Starting Nanobot Streamlit UI...
cd /d "%~dp0"
streamlit run streamlit_app/app.py --server.port 8501
pause