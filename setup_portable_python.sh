#!/bin/bash
echo "Setting up Portable Python Environment for Autonomous Trader..."
python3 -m venv Python/venv
source Python/venv/bin/activate
pip install --upgrade pip
pip install pandas numpy yfinance xgboost faiss-cpu cryptography beautifulsoup4 requests sqlite3 scikit-learn scipy statsmodels
echo "Environment Ready."
