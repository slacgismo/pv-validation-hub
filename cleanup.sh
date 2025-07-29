#!/usr/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Remove all existing files from the various directories associated with development for a clean environment

# Remove all files from the workers directory

WORKERS_DIR='./workers'

WORKER_CURRENT_EVALUATION_DIR="${WORKERS_DIR}/current_evaluation"
WORKER_LOGS_DIR="${WORKERS_DIR}/logs"
WORKER_TMP_DIR="${WORKERS_DIR}/tmp"

if [ -d "${WORKER_CURRENT_EVALUATION_DIR}" ]; then
    rm -rf "${WORKER_CURRENT_EVALUATION_DIR:?}/"*
fi

if [ -d "${WORKER_LOGS_DIR}" ]; then
    rm -rf "${WORKER_LOGS_DIR:?}/"*
fi

if [ -d "${WORKER_TMP_DIR}" ]; then
    rm -rf "${WORKER_TMP_DIR:?}/"*
fi

echo "Cleaned up Worker directories"

# Remove all files from the valhub directory

VALHUB_DIR='./valhub'

VALHUB_LOGS_DIR="${VALHUB_DIR}/logs"
VALHUB_MEDIA_DIR="${VALHUB_DIR}/media"

if [ -d "${VALHUB_LOGS_DIR}" ]; then
    rm -rf "${VALHUB_LOGS_DIR:?}/"*
fi

if [ -d "${VALHUB_MEDIA_DIR}" ]; then
    rm -rf "${VALHUB_MEDIA_DIR:?}/"*
fi

echo "Cleaned up Valhub directories"

# Remove all files from the s3Emulator directory

S3_DIR='./s3Emulator'
S3_BUCKET_DIR="${S3_DIR}/valhub-bucket"

S3_DATA_DIR="${S3_BUCKET_DIR}/data_files"
S3_FILES_DIR="${S3_DATA_DIR}/files"
S3_REFERENCE_DIR="${S3_DATA_DIR}/references"

if [ -d "${S3_FILES_DIR}" ]; then
    rm -rf "${S3_FILES_DIR:?}/"*
fi

if [ -d "${S3_REFERENCE_DIR}" ]; then
    rm -rf "${S3_REFERENCE_DIR:?}/"*
fi

S3_EVALUATION_SCRIPTS_DIR="${S3_BUCKET_DIR}/evaluation_scripts"

if [ -d "${S3_EVALUATION_SCRIPTS_DIR}" ]; then
    rm -rf "${S3_EVALUATION_SCRIPTS_DIR:?}/"*
fi

S3_SUBMISSION_FILES_DIR="${S3_BUCKET_DIR}/submission_files"

if [ -d "${S3_SUBMISSION_FILES_DIR}" ]; then
    rm -rf "${S3_SUBMISSION_FILES_DIR:?}/"*
fi

echo "Cleaned up S3 directories"

# Remove all files from the frontend directory

FRONTEND_DIR='./pv-validation-hub-client'

FRONTEND_ANALYSIS_ASSETS_DIR="${FRONTEND_DIR}/public/static/assets/analysis"

# Where folder is a number, e.g., 1, 2, 3, etc. 

if [ -d "${FRONTEND_ANALYSIS_ASSETS_DIR}" ]; then
    # Remove all numbered folders inside the analysis assets directory
    find "${FRONTEND_ANALYSIS_ASSETS_DIR}" -mindepth 1 -maxdepth 1 -type d -regex '.*/[0-9]+' -exec rm -rf {} +
fi

# if [ -d "${FRONTEND_ANALYSIS_ASSETS_DIR}" ]; then
#     rm -rf "${FRONTEND_ANALYSIS_ASSETS_DIR:?}/"*
# fi

echo "Cleaned up Frontend directories"

# Remove all files from the ec2 directory

EC2_DIR='./ec2'

EC2_EVALUATION_SCRIPTS_DIR="${EC2_DIR}/evaluation_scripts"

if [ -d "${EC2_EVALUATION_SCRIPTS_DIR}" ]; then
    rm -rf "${EC2_EVALUATION_SCRIPTS_DIR:?}/"*
fi

echo "Cleaned up EC2 directories"

echo "Cleanup complete"
