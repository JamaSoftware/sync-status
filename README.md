# Jama Software
## Sync Status Script

This script will allow the user to determine if certain items are in sync.  The script takes as input a filter ID.
Then all the items that are in the filter are checked for synced items, for each synced item found the status of the
sync is output to a row in a csv file at the specified output location.

# Requirements
* [python 3.7+](https://www.python.org/downloads/)
* [Pipenv](https://docs.pipenv.org/en/latest/) 

## Installing dependencies 
 * Download and unzip the package contents into a clean directory.
 * execute pipenv install from the commandline.
 
## Usage
 * Open the config.py file in a text editor and set the relevant settings for your environment.
 * Open the terminal to the directory the script is in and execute the following:   
 ```
 pipenv run python check_sync_status.py
 ```