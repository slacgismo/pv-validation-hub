#!/bin/bash

chmod +x *

# Order matters for some of these. Files need associated systems to exist. Submissions need a user and an analysis. 

# Django manages primary keys. Any systems imported from elsewhere will go to the next chronological number. Therefore, this script should only be used for first-time setup. 
# It can guide future automation.

./create_user.sh || { echo "create_user.sh failed"; exit 1; }

./create_analysis.sh || { echo "create_analysis.sh failed"; exit 1; }

# ./create_systemmetadata.sh || { echo "create_systemmetadata.sh failed"; exit 1; }

# ./create_file_metadata.sh || { echo "create_file_metadata.sh failed"; exit 1; }

# ./create_validation.sh || { echo "create_validation.sh failed"; exit 1; }

./create_submissions.sh || { echo "create_submissions.sh failed"; exit 1; }

echo "Preload completed!"
