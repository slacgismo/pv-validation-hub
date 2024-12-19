# time-shift-validation-hub

This repo is an example pipeline for running a validation test in the PV Validation Hub. Specifically,
this test covers time shift estimation & validation. The explanation for the scripts are as follows:

pvinsight-time-shift-runner.py: This the main runner script for executing a particular validation test.
It aggregates all of the information from the tables, loads in the developer-submitted module to test against,
and runs the module against the validation data. Finally, it takes the results of the validation run,
aggregates them, and creates public and private reports for feeding back into the database and
disseminating to the developer, respectively.

pvanalytics_cpd_module.py: This is an example of a user-submitted module. This module would be loaded into
the pvinsight-time-shift-runner and tested against with the validation data.

pvanalytics_osd_module.py: This is an example of a user-submitted module. This module would be loaded into
the pvinsight-time-shift-runner and tested against with the validation data.

sdt_module.py: This is an example of a user-submitted module. This module would be loaded into
the pvinsight-time-shift-runner and tested against with the validation data.

proposed-test-infrastructure-erd.PNG: This file shows the relationships between the proposed tables in
the test structure. Examples of these tables are shown in the /data/ folder.

/data/ folder: This folder contains all of the information for running the validation test. In particular,
the folder contains the following:
	- /file_data/ csv's: These are the raw time series input files that are passed to the module for
		each individual test. 
	- /validation_data/ csv's: These are the output files that we compare to (ground-truth files) when
		we benchmark each module output (this allows us to calculate error metrics for each example)
	- system_metadata.csv: This is a representation of what could site in the system_metadata table. This
		file contains information of system metadata (latitude, longitude, elevation, etc). A system
		represents a physical solar site. Multiple files can be associated with a single system.
	- file_metadata.csv: This is a representation of what could sit in the file_metadata table. This
		contains metadata information associated with each file. It also links to the system_metadata
		table via the system_id
	- validation_tests.csv: This file represents the validation_tests table. It includes information
		on specific validation tests run the Valdiation Hub, such as time shift detection or
		azimuth-tilt estimation. Each validation tests has its own unique row.
	- file_test_link.csv: This file links unique file IDs to a particular validation_test ID (links files
		to the validation test that we want to run)

/results/ folder: This folder contains files related to public and private reporting. Specifically, the data
in time-shift-public-metrics.json would feed into a final 'public results' table with general information
on the module run (average run speed, average MAE, requirements for running function, etc). The associated .png
files in this folder would be used in private reporting and sent directly to the developer who submitted the
module.
