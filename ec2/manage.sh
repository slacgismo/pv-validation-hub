#!/usr/bin/bash

set -euo pipefail
IFS=$'\n\t'

function usage() {
    echo "Usage: $0 {insert} <analysis-task-name> [--dry-run] [--force] [--prod] [--limit <number>]"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

DRY_RUN=False
FORCE=False
LIMIT=0
PROD=False


TASK_DIR=./analysis-tasks

COMMAND=$1
TASK_FOLDER_NAME=$2
shift 2

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=True ;;
        --force) FORCE=True ;;
        --limit) LIMIT=$2; shift ;;
        --prod) PROD=True ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done

TASK_FOLDER_DIR=$TASK_DIR/$TASK_FOLDER_NAME

if [ "$COMMAND" == "insert" ]; then
    if [ -z "$TASK_FOLDER_DIR" ]; then
        echo "Missing directory"
        usage
    fi
fi

case "$COMMAND" in
    insert)
        python3 insert_analysis.py --dry-run $DRY_RUN --force $FORCE --limit "$LIMIT" --prod $PROD --dir "$TASK_FOLDER_DIR" ;;
    *)
        usage
        ;;
esac

