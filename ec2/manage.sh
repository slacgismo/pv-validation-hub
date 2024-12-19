#!/usr/bin/bash

set -euo pipefail
IFS=$'\n\t'

function usage() {
    echo "Usage: $0 {insert} {time-shift-detection|az-tilt-estimation} [--dry-run] [--force] [--prod] [--limit <number>]"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

DRY_RUN=False
FORCE=False
LIMIT=0
PROD=False

TASK_DIR="./analysis-tasks"
TIME_SHIFT_DIR="$TASK_DIR/time-shift-detection"
AZ_TILT_DIR="$TASK_DIR/az-tilt-estimation"

COMMAND=$1
TASK=$2
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

case "$COMMAND" in
    insert)
        case "$TASK" in
            time-shift-detection)
                echo "Inserting time-shift-detection task"
                python3 insert_analysis.py --dry-run $DRY_RUN --force $FORCE --limit $LIMIT --prod $PROD --dir $TIME_SHIFT_DIR
                ;;
            az-tilt-estimation)
                echo "Inserting az-tilt-estimation task"
                python3 insert_analysis.py --dry-run $DRY_RUN --force $FORCE --limit $LIMIT --prod $PROD --dir $AZ_TILT_DIR
                ;;
            *)
                usage
                ;;
        esac
        ;;
    *)
        usage
        ;;
esac

