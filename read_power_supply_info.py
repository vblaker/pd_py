import csv
import datetime as dt

debug = 0
data_dictionary = {}

with open('power_supply_info.csv', 'r') as csv_file:
    readCSV = csv.reader(csv_file, delimiter=',')
    for row in readCSV:
        if row:
            if 'TimeStamp' in row:
                # Reset / init lists and dictionaries
                header_list = []
                header_dictionary = {}
                data_dictionary = {}

                # DATA VALIDATION: Check for non-empty headers
                for i in range(len(row)):
                    if row[i]: header_list.append(row[i])
                if debug == 1: print(header_list)

                # Identify all the Column Headers
                header_dictionary = dict(zip(header_list, range(len(header_list))))     # Create header dictionary
                data_dictionary = {key: [] for key in header_dictionary}                # Init data dictionary

            if data_dictionary:
                try:
                    time_stamp_str = row[header_dictionary['TimeStamp']]        # Find column TimeStamp and get value
                    test = int(time_stamp_str[:4])                              # Slice first 4 chars (YEAR) and TEST
                    time_stamp = dt.datetime.strptime(time_stamp_str, '%Y-%m-%d-%H:%M:%S.%f')
                    if debug == 1:
                        print(time_stamp)
                    for header in header_dictionary:                                        # Append values to data dictionary
                        data_dictionary[header].append(row[header_dictionary[header]])
                except ValueError:
                    if debug == 1:
                        print('Skipping row {0}'.format(row))

if debug == 1:
    print(data_dictionary)
