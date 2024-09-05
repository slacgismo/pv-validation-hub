Worker error classification for private reports. These are generic error types for use in private reports. This is intended to be separate from the complete run logs saved into the submission folder in s3. These error codes and messages should be documented here, for all codes included in the ```errorcodes.json``` file inside the worker.

# Operational Errors

This is for catching http and other system operational issues. These "pass-through" type errors 
are intended to let a user know when a failure is not necessarily their fault.

op1 = 
op2 = 
op3 = 
op4 = 
...
op121 =

# Submission Wrapper Errors

Wrapper errors are intended for catching basic issues in a submission's structure and returns. 
This is for reporting when requirements for our runner are missing from the wrapper.

wr1 = missing requirements.txt file
wr2 = requirements file includes invalid package names
wr3 = missing "wrapper" .py file
wr4 = cannot find files(improper compression structure)
wr5 = 
wr6 = 
wr7 = 

# Submission Internal Errors

Submission errors are intended to be generic errors returned from a submission.

sb1 = 
sb2 = 
sb3 = 
sb4 = 