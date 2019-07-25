#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import json
import platform
import argparse

# Global for verbose logging, controlled by --verbose argument
VERBOSE = False

# Globals to denote if latency_info2 or latency_info is parsed for latency
# data from the analytics. Can be changed by the --lat-info argument
LAT_TIME_KEY = 'ended'
LAT_INFO_KEY = 'latency_info2'

def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('CSV', nargs='+')
    argparser.add_argument('-L', '--lat-csv', action='store_true', help='Generate CSV for Latency Steps in Assembly')
    argparser.add_argument('-i', '--lat-info', action='store_true', help='Use latency_info instead of latency_info2')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = argparser.parse_args()
    if args.verbose:
        global VERBOSE
        VERBOSE = True
        print(args)
    if args.lat_info:
        global LAT_TIME_KEY
        global LAT_INFO_KEY
        LAT_TIME_KEY = 'started'
        LAT_INFO_KEY = 'latency_info'
        if VERBOSE:
            print('Using latency_info for latency data, instead of latency_info2')
            print('Switching latency time key from {0} to {1}'.format('ended', 'started'))
    return args

def load_csv(csv_file):
    print('Loading file: ' + csv_file)
    with open(csv_file) as csv_open:
        csv_rows = csv.DictReader(csv_open)
        rows = []
        for row in csv_rows:
            rows.append(row)
        if VERBOSE:
            print('{0} row(s) loaded from CSV'.format(len(rows)))
        return rows

def default_output(rows):
    for row in rows:
        api_name = row['api_name']
        latinfo = json.loads(str(row[LAT_INFO_KEY]))
        tid = row['transaction_id']
        tts = row['time_to_serve_request']
        ts = row['@timestamp']
        tasks = ''
        for obj in latinfo:
           tasks = tasks + obj[u'task'] + '=' + str(obj[u'{0}'.format(LAT_TIME_KEY)]) + ','
        print(tts + ',' + ts + ',' + tid + ',' + api_name + ',' + tasks[:-1])

def split_apis(rows):
    apis = {}
    for row in rows:
        api_name = row['api_name']
        if api_name not in apis:
            apis[api_name] = []
        apis[api_name].append(row)
    if VERBOSE:
        for api in apis:
            print('{0} has {1} analytics entries'.format(api, len(apis[api])))
    return apis

def get_latency_info(row):
    lat_raw = row[LAT_INFO_KEY]
    lat_json = json.loads(str(lat_raw))
    lat_info = []
    for entry in lat_json:
        new_entry = dict()
        new_entry['task'] = entry[u'task'].encode('utf-8')
        new_entry[LAT_TIME_KEY] = entry[u'{0}'.format(LAT_TIME_KEY)]
        lat_info.append(new_entry)
    if VERBOSE:
        print('Raw latency info: {0}'.format(lat_raw))
        print('Decoded latency info: {0}'.format(str(lat_info)))
    return lat_info

def get_fieldnames(row):
    lat_info = get_latency_info(row)
    fieldnames = []
    for entry in lat_info:
        fieldnames.append(entry['task'])
    if VERBOSE:
        print('Fieldnames: {0}'.format(str(fieldnames)))
    return fieldnames

def convert_lat_info_to_csv(lat_info):
    row = []
    lat_time = 'ended'
    for entry in lat_info:
        row.append(entry[lat_time])
    if VERBOSE:
        print('Latency CSV row: {0}'.format(row))
    return row

def generate_lat_csv(csv_name, api, rows):
    fieldnames = get_fieldnames(rows[0])
    if len(fieldnames) > 0:
        out_file = '{0}-{1}-latency.csv'.format(csv_name, api)
        print('Generating latency CSV for API: {0}'.format(api))
        if VERBOSE:
            print('Output file will be: {0}'.format(out_file))
        with open(out_file, 'w') as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(fieldnames)
            for row in rows:
                lat_info = get_latency_info(row)
                csv_row = convert_lat_info_to_csv(lat_info)
                writer.writerow(csv_row)
        if VERBOSE:
            print('Successfully written latency data to {0}'.format(out_file))
        return out_file
    else:
        if VERBOSE:
            print('Cannot generate latency CSV for API: {0}'.format(api))
        return None

def main():
    args = parse_args()
    for csv_file in args.CSV:
        csv_name = os.path.splitext(csv_file)[0]
        csv_rows = load_csv(csv_file)
        if args.lat_csv:
            apis = split_apis(csv_rows)
            out_files = []
            for api in apis:
                out_file = generate_lat_csv(csv_name, api, apis[api])
                out_files.append(out_file)
            print('Successfully generated the following output files:')
            for filename in out_files:
                if filename is not None:
                    print(filename)
        else:
            default_output(csv_rows)

if __name__ == '__main__':
    main()
