import sys
import os
import csv
from py_jama_rest_client.client import JamaClient

import config

j_client = JamaClient(config.JAMA_CONNECT_URL, (config.USERNAME,config.PASSWORD))

# The header names for the CSV output.
field_names = ['ID', 'Global ID', 'Name', 'Synced Item', 'Synced Project', 'inSync?']


def check_sync(filter_id, project_id, output_location):
    # get all the items for this filter.
    filter_results = j_client.get_filter_results(filter_id, project_id)

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
    for item in filter_results:
        item_id = item['id']
        synced_items = j_client.get_items_synceditems(item_id)

        if len(synced_items) == 0:
            items_without_sync += 1
            print('item: {} has no synced items.'.format(item_id))

        # For each item this item is synced with, check if the two are in sync
        for sync_item in synced_items:
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

    print('\n*** Process Complete ***')
    print('There were {} items in the filter.'.format(total_results))
    print('{} of the items had no synced items associated with them.'.format(items_without_sync))
    print('{} pairs of items are in sync.'.format(items_in_sync))
    print('{} pairs of items are not in sync'.format(items_out_of_sync))


if __name__ == "__main__":
    check_sync(config.filter_id, config.filter_project_id, config.output_location)

