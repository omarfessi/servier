#!/bin/bash
# set -e
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function clean-data-dir {
    echo "Cleaning contents of corrupted_data, gold_zone, and silver_zone directories..."
    find "$THIS_DIR/data/corrupted_data" -type f -print -exec rm -rf {} +
    find "$THIS_DIR/data/gold_zone" -type f -print -exec rm -rf {} +
    find "$THIS_DIR/data/silver_zone" -type f -print -exec rm -rf {} +
    echo "Directories cleaned: corrupted_data, gold_zone, silver_zone."
}

function help {
    echo "Available tasks:"
    compgen -A function | cat -n
}

function test:wheel-locally {
    echo "Creating a new virtual environment called .venvtest..."
    rm -rf .venvtest || true
    python -m venv .venvtest
    source .venvtest/bin/activate
    echo "Checking in which environement python is installed.. $(which python)"
    pip install --upgrade pip
    rm -rf dist build || true
    find . -type d \( -name "*egg-info" -o -name "*.dist-info" \) -exec rm -rf {} + || true
    echo "Installing dev/build dependecies in the virtual environment..."
    pip install -r "$THIS_DIR"/requirements-dev.txt
    echo "Building the wheel..."
    python -m build --sdist --wheel "$THIS_DIR/"
    pip install ./dist/*.whl
    echo "Running tests..."
    python -m pytest -vv -s ${@:-"$THIS_DIR/tests/"}
}

function install:dev-mode {
    echo "Installing the project in dev mode..."
    python -m venv .venvtest
    python -m pip install --upgrade pip
    pip install --editable "$THIS_DIR/[dev]"
}

function lint {
    echo "Running lint checks..."
}


# Task execution logic
if [[ $# -eq 0 ]]; then
    echo "No task provided. Use './run.sh help' for available tasks."
    exit 1
fi

TASK=$1
shift

if declare -F "$TASK" > /dev/null; then
    "$TASK" "$@" # Call the function with any additional arguments
else
    echo "Unknown task: $TASK"
    echo "Use './run.sh help' for available tasks."
    exit 1
fi
