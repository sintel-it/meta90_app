@echo off
cd /d "%~dp0\.."
venv\Scripts\python.exe scripts\predeploy_check.py
