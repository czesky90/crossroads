import sys
import os
from datetime import datetime
import json

print("Start")
file_path = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
# start_timestamp = sys.argv[2]
# stop_timestamp = sys.argv[3]

start_timestamp = str(int(datetime.timestamp(datetime.strptime(start_date, '%Y-%m-%d'))) * 10)
stop_timestamp = str(int(datetime.timestamp(datetime.strptime(end_date, '%Y-%m-%d'))) * 10)


file_name = os.path.basename(file_path)
dirname = os.path.dirname(file_path)

print("Loading file..")
with open(file_path) as json_file:
    json_content = json.load(json_file)

print("Searching timestamps")
new_locations = {'locations': []}
start_extraction = False
count_timestamps = 0
for location in json_content['locations']:
    if not start_extraction:
        if location['timestampMs'] >= start_timestamp:
            start_extraction = True
            print("Started extraction from timestamp: {}".format(location['timestampMs']))
            new_locations['locations'].append(location)
    else:
        count_timestamps += 1
        new_locations['locations'].append(location)
        if location['timestampMs'] >= stop_timestamp:
            print("End extraction on timestamp: {}".format(location['timestampMs']))
            break

print("Extracted: {} timestamps from: {}".format(count_timestamps, file_name))

outfile_path = os.path.join(dirname, "extracted_" + file_name)
with open(outfile_path, 'w') as outfile:
    json.dump(new_locations, outfile)

print("Saved extracted data to: {}".format(outfile_path))