import csv

debug = 1

with open('power_supply_info.csv', 'r') as csv_file:
    readCSV = csv.reader(csv_file, delimiter=',')
    for row in readCSV:
        if row:
            if row[0] == 'TimeStamp':
                # Check for non-empty values
                header_list = []
                for i in range(len(row)):
                    if row[i]: header_list.append(row[i])
                #header_list = row[:-1]                                                  # Slice OFF last empty value

                if debug == 1: print(header_list)
                # Identify all the Column Headers
                header_dictionary = dict(zip(header_list, range(len(header_list))))     # Create header dictionary
                data_dictionary = {key: [] for key in header_dictionary}                # Init data dictionary
                continue
            try:
                test = int(row[0][:4])
                time_stamp = row[0]
                if debug == 1:
                    print(time_stamp)
                for header in header_dictionary:                                        # Append values to data dictionary
                    data_dictionary[header].append(row[header_dictionary[header]])
            except ValueError:
                    print('Skipping row {0}'.format(row))

print(data_dictionary)
