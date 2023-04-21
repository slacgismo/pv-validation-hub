#!/bin/bash

chmod +x *

./create_user.sh || { echo "create_user.sh failed"; exit 1; }

./create_analysis.sh || { echo "create_analysis.sh failed"; exit 1; }

./create_systemmetadata.sh || { echo "create_systemmetadata.sh failed"; exit 1; }

./create_file_metadata.sh || { echo "create_file_metadata.sh failed"; exit 1; }

./create_validation.sh || { echo "create_validation.sh failed"; exit 1; }

./create_submissions.sh || { echo "create_submissions.sh failed"; exit 1; }

echo "Preload completed!"