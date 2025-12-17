"""
BitShield - Transparent Procurement Agent
Streamlit UI Application

This is the main entry point for the web application.
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from ui.app import main

if __name__ == "__main__":
    main()
