#!/usr/bin/env python
"""
Quick Launcher for Araf's Assistant
Runs database migrations and starts the Django development server.
"""
import os
import sys
import subprocess

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 60)
    print("🤖 Starting Araf's Assistant (Django AI Chatbot) 🚀")
    print("=" * 60)

    # 1. Run migrations
    print("\n[1/2] Applying database migrations...")
    subprocess.run([sys.executable, "manage.py", "makemigrations", "accounts", "chatbot"])
    subprocess.run([sys.executable, "manage.py", "migrate"])

    # 2. Start server
    print("\n[2/2] Launching server on http://127.0.0.1:8000 ...")
    print("👉 Open in your browser: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server.\n")
    
    try:
        subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == "__main__":
    run()
