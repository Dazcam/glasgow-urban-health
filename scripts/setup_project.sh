#!/bin/bash

# 1. Create Directory Structure
echo "Creating directory structure..."
mkdir -p data/raw data/processed src scripts environment

# 2. Create Placeholder Files
touch src/app.py
touch environment/requirements.txt
touch README.md
touch .gitignore

# 3. Populate .gitignore
echo "__pycache__/
*.py[cod]
.DS_Store
data/raw/*
data/processed/*
!data/**/*.gitkeep" > .gitignore

# 4. Create .gitkeep files (to track empty folders in Git)
touch data/raw/.gitkeep
touch data/processed/.gitkeep

echo "Project structure created successfully."
