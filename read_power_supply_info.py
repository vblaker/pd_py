import csv

#for line in reversed(open("filename").readlines()):
#    print line.rstrip()

debug = 1

with open('power_supply_info.csv', 'r') as csv_file:
    readCSV = csv.reader(csv_file, delimiter=',')
    for row in readCSV:
        if row:
            if row[0] == 'TimeStamp':
                header_list = row
                print(header_list)
                # Identify all the Column Headers
                header_dictionary = dict(zip(header_list, range(len(header_list))))     # Create header dictionary
                data_dictionary = {}
                data_dictionary = {header: [] for header in header_list}    # Init data dictionary
                continue
            try:
                time_stamp = row[0]
                print(int(time_stamp[:4]))
                # Append values to data dictionary
                for header in header_list:
                    data_dictionary[header].append(row[header_dictionary[header]])
            except ValueError:
                    print('Skipping row {0}'.format(row))
