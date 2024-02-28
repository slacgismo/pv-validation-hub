# Validation Hub Administration

In order to keep a distinct separation between what should allow public access, and what should not, the validation hub utilizes two separate s3 buckets. The ```pv-validation-hub-website```(pvhw) bucket is the public-facing website bucket, and contains nothing that would be an issue if exposed. The ```pv-validation-hub-bucket```(pvhb) is our private file-storage bucket, which will contain the validation files themselves as well as user private results. The general layout of these buckets is listed in the json below.

~~~
pvhw {
    assets {
        1 {
            md1,
            md2,
            etc...
        }
    },
    static {},
    index.html
}
___________________
pvhb {
    eval {
        1 {
            config,
            eval.py,
            etc...
        }
    },
    data {
        analytical {},
        ground_truth
    },
    submission {
        user {
            submission1 {
                results {},
                tar.gz
            }
        }
    }

}
~~~

In order to maintain and update our buckets, we will need a combination of resources to allow easily integrated updates for our public and private data.

This requires the following documentation to help clarify the process for administering new analyses and maintaining old ones.

## Adding New Analyses

Adding a new analysis is a multi-step process. Analyses have a number of dependencies in order to be correctly setup, and its current state is open for improvement and discussion. Each section below covers a distinct part of the process.

### Adding Markdown Analysis descriptors

When a user accesses a page on an s3 bucket-hosted website, the browser downloads the static files from the S3 bucket and executes the JavaScript code to build and display the content on the client-side(user's system). This leaves us a few options. 

The md files must follow a standardized naming scheme with the containing folder ID being the only variable, for modular access and ease of programming. This is consistent across both approaches.

~~~
{
    ... {
        1 {
            dataset.md,
            rules.md,
            overview.md,
            summary.md

        }
    }
}
~~~

> **DISCUSSION POINTS**
>
> - (Preferred) This method requires more administrative overhead, but is programmatically easier to implement. In the ```frontend/public/assets/``` directory, create a new directory for your md documents. The directory name should match the directory name for the same analysis(e.g. an analysis in folder "1" should have website md docs in folder "1"). This would be very beneficial for clearly defined organization, while also guaranteeing quick and stable access to the files. This would allow very easy sync updates for the frontend portion of the application and updating just descriptors without any extensive work.
>
> - Optionally, storing all the md files in the private s3 bucket with their respective analytical task runners can be done. This would require some additional developmental steps to pull that data from the API and would increase server-load, as the front-end would need to make additional queries to pull the md files for each task instead of including them by default. This makes organization and administration much simpler in exchange for additional programmatic overhead and refactoring.




### Adding Analysis scripts and config

This portion is necessary for any analysis to show up on the validation hub.

The current process is to add all the analysis files into our pvhb s3 bucket and to send a post request to the ```/analysis/create/``` route. The current implementation stores all analysis descriptors in the database. 

> **DISCUSSION POINTS**
>
> - Utilizing standardized MD files simplifies some of the of the process to create a new analysis, as we can reduce the number of variables that we need to define when calling the analysis create route. (I am also looking into setting a *bucket event* or alternative method, such as an admin authenticated *lambda* function, to call this route. Currently it can only be called within the VPC network.)
>
> - The example below demonstrates adding the new analysis folder. This is done by adding one to the latest folder ID, and then running the analysis creation script.
    ~~~
    pvhb {
        eval {
            1 {
                config,
                eval.py,
                etc...
            },
            2 {
                ...
            }
        },
        ...
    }
    ~~~
>
> - Script with description definitions removed
    ~~~
    #!/bin/bash

    API_URL="http://api:8005/analysis/create/"
    analysis_name="Time Shift Analysis"
    EVALUATION_SCRIPT_PATH="/pv-validation-hub-bucket/evaluation_scripts/3/pvinsight-time-shift-runner.py"
    MAX_CONCURRENT_SUBMISSION_EVALUATION="100"

    curl -X POST -H "Content-Type: multipart/form-data" \
    -F "analysis_name=$analysis_name" \
    -F "evaluation_script=@$EVALUATION_SCRIPT_PATH" \
    -F "max_concurrent_submission_evaluation=$MAX_CONCURRENT_SUBMISSION_EVALUATION" \
    $API_URL
    ~~~

> Potential improvement:
> 
> Update the analysis creation route to accept verified IAM user requests or another form of authentication, and have the route automatically create the id-based directory to store the analysis and associated config and file-test linker. Will require more programming overhead but can incredibly simplify and standardize the admin process. Adding a simple UI hosted within an authorized EC2 and granting direct access only to admins is another method.

## Adding new files

There are routes for adding each file type and storing the metadata in the database. The ```API_BASE_URL``` can be changed to accept an input (e.g. api.pv-validation-hub.org). The preloader scripts can also be used to add new files, not just the initial batch being loaded. This can be added as part of the simple admin UI mentioned earlier, or a validated admin request. 

file metadata:
~~~
#!/bin/bash

API_BASE_URL="http://api:8005/file_metadata/filemetadata/"

# Read the CSV file and skip the header
tail -n +2 file_metadata.csv | while IFS=, read -r file_id system_id file_name timezone data_sampling_frequency issue subissue
do
  # Use a default value for empty subissue
  if [ -z "$subissue" ]; then
    subissue="N/A"
  fi

  # Create a JSON object from the CSV row
  json_data=$(jq -n \
                --arg file_id "$file_id" \
                --arg system_id "$system_id" \
                --arg file_name "$file_name" \
                --arg timezone "$timezone" \
                --arg data_sampling_frequency "$data_sampling_frequency" \
                --arg issue "$issue" \
                --arg subissue "$subissue" \
                '{file_id: $file_id | tonumber, system_id: $system_id | tonumber, file_name: $file_name, timezone: $timezone, data_sampling_frequency: $data_sampling_frequency | tonumber, issue: $issue, subissue: $subissue}')

  # Upload the JSON data to the API
  curl -X POST -H "Content-Type: application/json" -d "$json_data" "$API_BASE_URL"
  echo ""
done
~~~

system metadata:
~~~
#!/bin/bash

API_URL="http://api:8005/system_metadata/systemmetadata/bulk_create/"

# Remove the header from the CSV and convert it to JSON
tail -n +2 system_metadata.csv | awk -F, 'BEGIN {print "["} NR>1 {printf ", "} {
    printf "{\"system_id\": %d, \"name\": \"%s\", \"azimuth\": %f, \"tilt\": %f, \"elevation\": %f, \"latitude\": %f, \"longitude\": %f, \"tracking\": %s, \"climate_type\": \"%s\", \"dc_capacity\": %f}", $1, $2, $3, $4, $5, $6, $7, tolower($8), $9, $10
} END {print "]"}' > system_metadata.json

# Upload the JSON data to the API
curl -X POST -H "Content-Type: application/json" -d "@system_metadata.json" "${API_URL}"

# Clean up the temporary JSON file
rm system_metadata.json
~~~

validation:
~~~
#!/bin/bash

API_BASE_URL="http://api:8005/validation_tests"
CSV_FILE="validation_tests.csv"
API_UPLOAD_URL="${API_BASE_URL}/upload_csv/"

if ! command -v curl &> /dev/null
then
    echo "curl command not found. Please install curl and try again."
    exit 1
fi

curl -X POST -H "Content-Type: multipart/form-data" -F "file=@${CSV_FILE}" ${API_UPLOAD_URL}
~~~

IDs in the postgres database start at 1 and automatically increment by 1 for each new item added. A viewer could be added for long-term maintenance and ease for configuring the necessary file-linkers, as well as simplifying validation that the files being selected by the linker are the correct files.

While we currently are pulling the whole s3 folder with the files inside, we can adjust to implement reading each file from s3 with pandas, as each file has a unique name that can be extracted from the file metadata selected by the file linker.

A great option for enhancing this process would be to add a lambda route that requires a validated IAM role to access. This lambda route can be configured for public access to allow us to call it after validating our access, and we can configure it to accept the csv files we want to use to load new metadata in the database. The lambda route can then automate processing the csv files using the above scripts and can add a secure layer for us to call sensitive API routes within the VPC. 
