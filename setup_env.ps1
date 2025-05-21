# Create virtual environment
python -m venv venv

# Activate the venv
& ".\venv\Scripts\Activate.ps1"

# Install requirements
pip install scikit-rf pyqt5 matplotlib numpy

# Start The Program
python PySmiCha.py