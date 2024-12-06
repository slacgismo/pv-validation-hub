#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

function usage() {
    echo "Usage: $0 {insert} [--dry-run] [--force] [--limit <number>]"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

COMMAND=$1
shift

DRY_RUN=False
FORCE=False
LIMIT=0
PROD=False

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

case "$COMMAND" in
    insert)
        echo "Inserting analysis..."
        echo "DRY_RUN=$DRY_RUN, FORCE=$FORCE, LIMIT=$LIMIT, PROD=$PROD"
        python3 insert_analysis.py \
            --dry-run $DRY_RUN --force $FORCE --limit $LIMIT --prod $PROD
        ;;
    *)
        usage
        ;;
esac

