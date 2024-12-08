#!/bin/bash
set -e
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function help {
    echo "Available tasks:"
    compgen -A function | cat -n
}

function data-dir:clean {
    echo "Cleaning contents of corrupted_data, gold_zone, and silver_zone directories..."
    find "$THIS_DIR/data/corrupted_data" -type f -print -exec rm -rf {} +
    find "$THIS_DIR/data/gold_zone" -type f -print -exec rm -rf {} +
    find "$THIS_DIR/data/silver_zone" -type f -print -exec rm -rf {} +
    echo "Directories cleaned: corrupted_data, gold_zone, silver_zone."
}

function data-dir:create {
    echo "Creating the data folder structure..."
    ROOT_DIR="data"
    mkdir -p "$ROOT_DIR/corrupted_data"
    mkdir -p "$ROOT_DIR/gold_zone"
    mkdir -p "$ROOT_DIR/landing_zone"
    mkdir -p "$ROOT_DIR/silver_zone"
    # git submodule add --force https://github.com/omarfessi/servier-data
    mv servier-data/* "$ROOT_DIR/landing_zone/"
}
function virtualenv:create {
    ENV_NAME="${@:-.venvtest}"  
    echo "Creating and Activating the virtual environment called $ENV_NAME..."
    
    if [ ! -d "$ENV_NAME" ]; then

        python -m venv "$ENV_NAME"
    fi 

    source "$ENV_NAME/bin/activate"
    echo "Virtual environment $ENV_NAME activated. and python is installed at $(which python)"

}

function virtualenv:delete {
    ENV_NAME="${@:-.venvtest}" 
    echo "Deleting $ENV_NAME environment..."
    if [ -d $ENV_NAME ]; then
        rm -rf $ENV_NAME
        echo "$ENV_NAME directory removed."
    else
        echo "$ENV_NAME does not exist."
    fi 
}

function clean:build {
    echo "Cleaning build artifacts..."
    rm -rf dist build || true
    find . -type d \( -name "*egg-info" -o -name "*.dist-info" \) -exec rm -rf {} + || true
}

function wheel:build { 
    echo "Building the wheel..."
    python -m build --sdist --wheel "$THIS_DIR/"
}

function wheel:install {
    echo "Installing the wheel..."
    pip install ./dist/*.whl
}

function test:wheel-locally {
    virtualenv:delete
    virtualenv:create
    echo "Checking in which environement python is installed.. $(which python)"
    pip install --upgrade pip
    clean:build
    echo "Installing dev/build dependecies in the virtual environment .venvtest..."
    pip install -r "$THIS_DIR"/requirements-dev.txt
    echo "Building the wheel..."
    wheel:build
    wheel:install
    test:unit-tests
}

function install:dev-mode {
    echo "Installing the project in dev mode..."
    echo "Creating and Activating the virtual environment called .venv..."
    python -m venv .venv
    python -m pip install --upgrade pip
    pip install --editable "$THIS_DIR/[dev]"
}

function lint {
    echo "Running lint checks..."
    #TODO: Add linters
}

function test:unit-tests {
    echo "Running tests..."
    python -m pytest -vv -s ${@:-"$THIS_DIR/tests/"}
}

function servier-aggregate:main-pipeline {
    virtualenv:create
    echo "Running servier-aggregate main pipeline..."
    servier-aggregate main-pipeline  --raw-pubclinical-data=data/landing_zone/publications_data --raw-drug-data=data/landing_zone/referential_data --silver-zone-path=data/silver_zone --trash-zone-path=data/corrupted_data
}

function servier-aggregate:journal-with-max-drugs {
    virtualenv:create
    echo "Running servier-aggregate journal-with-max-drugs pipeline..."
    servier-aggregate journal-with-max-drugs --silver-zone-path=data/silver_zone --gold-zone-path=data/gold_zone
}

function servier-aggregate:get-drugs-from-journals-that-mention-a-specific-drug {
    virtualenv:create
    echo "Running servier-aggregate get-drugs-from-journals-that-mention-a-specific-drug pipeline..."
    servier-aggregate get-drugs-from-journals-that-mention-a-specific-drug "$@" --silver-zone-path=data/silver_zone --gold-zone-path=data/gold_zone
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

