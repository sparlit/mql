@echo off
echo Setting up Portable Python Environment for Autonomous Trader...
python -m venv Python\venv
call Python\venv\Scripts\activate
pip install --upgrade pip
pip install pandas numpy yfinance xgboost faiss-cpu cryptography beautifulsoup4 requests scikit-learn scipy statsmodels transformers torch
echo Environment Ready.
