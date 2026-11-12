#!/bin/bash
set -e

command -v python3 >/dev/null || { echo "Python 3 is required"; exit 1; }
python3 -m pip install -r requirements.txt
echo "Done. Run: python3 scraper.py --site perplexity --prompts-csv prompts.csv"
