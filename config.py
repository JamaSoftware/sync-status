# Connection Settings
JAMA_CONNECT_URL = "https://instance.jamacloud.com"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
# If using oauth, set OAUTH = True, set USERNAME = "CLIENT_ID" and PASSWORD="CLIENT_SECRET"
OAUTH = False

# Input / Output settings
filter_id = 165

# if your filter is set to use 'Current Project' then you must supply a project_id. otherwise set to None
filter_project_id = None

# Enter the location for the output.
output_location = "./sync_status.csv"

# CSV Settings
# Output header row in CSV.  Must be set to True or False
csv_header = True

# A one character string to separate values.
delimiter = ','

# Logging date time format
log_date_time_format = "%Y-%m-%d %H_%M_%S"
