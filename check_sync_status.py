import sys
import os
import csv
import logging
import datetime
import progressbar
from time import sleep
from halo import Halo
from py_jama_rest_client.client import JamaClient

import config

# Wrap streams for progressbar
progressbar.streams.wrap_stderr()

# Setup logging
try:
    os.makedirs('logs')
except FileExistsError:
    pass

current_date_time = datetime.datetime.now().strftime(config.log_date_time_format)
log_file = 'logs/sync_status_' + str(current_date_time) + '.log'

logging.basicConfig(filename=log_file, level=logging.INFO)
log = logging.getLogger()

sync_logger = logging.getLogger('sync_status')
sync_logger.setLevel(logging.DEBUG)
sync_logger.addHandler(logging.StreamHandler(sys.stdout))

# Setup Jama Client
j_client = JamaClient(config.JAMA_CONNECT_URL, (config.USERNAME,config.PASSWORD))

# The header names for the CSV output.  if you change these you must update the row append dictionary below to match
field_names = ['ID', 'Global ID', 'Name', 'Synced Item', 'Synced Project', 'inSync?']


def check_sync(filter_id, project_id, output_location):
    # get all the items for this filter.
    sync_logger.info('Fetching items in filter {}, project: {}'.format(filter_id, project_id))

    spinner = Halo(text='Fetching filter data.', spinner='dots')
    spinner.start()
    filter_results = j_client.get_filter_results(filter_id, project_id)
    spinner.stop()

    # Give the output buffer a chance to clear
    sleep(0.2)

    total_results = len(filter_results)
    items_without_sync = 0
    items_in_sync = 0
    items_out_of_sync = 0

    # An array for the results
    rows = []

    # build up the project name lookup
    projects = j_client.get_projects()
    project_look_up = {}
    for project in projects:
        project_look_up[project['id']] = project['fields']['name']

    # Main Logic Here
    # For each item we want to find all item's it is synced with.
    for item in progressbar.progressbar(filter_results):
        item_id = item['id']
        synced_items = j_client.get_items_synceditems(item_id)

        if len(synced_items) == 0:
            items_without_sync += 1

        # For each item this item is synced with, check if the two are in sync
        for sync_item in synced_items:
            # Only check items that are in a project that is specified to check against.
            if len(config.project_list) > 0 and sync_item['project'] not in config.project_list:
                continue
            sync_item_id = sync_item['id']
            in_sync = j_client.get_items_synceditems_status(item_id, sync_item_id)

            if in_sync['inSync']:
                items_in_sync += 1
            else:
                items_out_of_sync += 1

            # Add the result of this comparison to as a row to CSV list to be written later
            rows.append({
                'ID': item['documentKey'],
                'Global ID': item['globalId'],
                'Name': item['fields']['name'],
                'Synced Item': sync_item['documentKey'],
                'Synced Project': project_look_up[sync_item['project']],
                'inSync?': in_sync['inSync']
            })

    # Write out the csv content.
    with open(output_location, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, delimiter=config.delimiter, fieldnames=field_names)
        if config.csv_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # Sleep to allow progressbar output buffer to catch up / flush
    sleep(0.2)
    sync_logger.info('*** Process Complete ***')
    sync_logger.info('There were {} items in the filter.'.format(total_results))
    sync_logger.info('{} of the items had no synced items associated with them.'.format(items_without_sync))
    sync_logger.info('{} pairs of items are in sync.'.format(items_in_sync))
    sync_logger.info('{} pairs of items are not in sync'.format(items_out_of_sync))


if __name__ == "__main__":
    check_sync(config.filter_id, config.filter_project_id, config.output_location)

