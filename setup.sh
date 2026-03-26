#!/usr/bin/env bash
set -euo pipefail

# This script sets up the environment for running the RunPod tools.

# Install UV if not already installed
if ! command -v uv &> /dev/null
then
    echo "UV could not be found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "UV installed."
else
    echo "UV is already installed."
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate
echo "Python: $(python --version)"

# Install dependencies
echo "Installing dependencies..."
# Sync dependencies from uv.lock
if [ -f "uv.lock" ]; then
  echo "Syncing dependencies via uv.lock"
  uv sync --extra dev --extra test --locked
else
  echo "No uv.lock found. Running uv sync anyway (will resolve dependencies)"
  uv sync --extra dev --extra test
fi

# Ensure prek is installed
if ! command -v prek >/dev/null 2>&1; then
  echo "Installing prek"
  uv tool install prek
fi

# Install prek hooks
if [ -f "prek.toml" ]; then
  echo "Installing prek hooks"
  prek install
else
  echo "WARNING: prek.toml not found. Skipping hook installation."
fi

echo "Setup complete ✔"
