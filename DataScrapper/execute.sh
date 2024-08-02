#!/bin/bash

# Check if enough arguments are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 filename limit"
  exit 1
fi

# Get the filename and limit from the command-line arguments
filename=$1
limit=$2

# Loop through each line in the specified file
while IFS= read -r search_term; do
  echo "Running command for: $search_term with limit $limit"
  ./venv/bin/python ./google-images-download/bing_scraper.py --search "$search_term" --limit $limit --download --chromedriver ./chromedriver.exe
done < "$filename"
