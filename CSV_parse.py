import csv
import numpy as np
from plot_data import *

#Define debug level
debug = 0

#PD Data Center SW

header_list = ['Time (s)', 'VBUS Voltage (V)', 'VBUS Current (A)', 'VCONN Voltage (V)',
               'VCONN Current (A)', 'CC1 Voltage (V)', 'CC1 Current (A)',
               'CC2 Voltage (V)', 'CC2 Current (A)']

# open(u'C:/Users/ra7621/Downloads/9V charging from Anker PD charger.tdc', True)        i# Open File
# export_iv(u'C:/Users/ra7621/Downloads/export.csv', {'session_id': 1L}, True)          # Export to CSV file


def ave(array):
    return sum(array)/len(array)


def stdev(array):
    return np.std(array)


def identify_column_headers(header_row, header_list, debug=0):
    header_dictionary = {}
    try:
        for k in range(0, len(header_row)):
            header_dictionary[header_list[k]] = header_row.index(header_list[k])
    except ValueError:
            print('Header Parsing Error: Not a FLOAT')

    if debug >= 1:
        print(header_dictionary)

    return header_dictionary

#Initialize arrays/lists
Time_stamp = []
VBUS_volts = []
VBUS_curr = []
VCONN_volts = []
VCONN_curr = []
CC1_volts = []
CC1_curr = []
CC2_volts = []
CC2_curr = []
data_list = [Time_stamp, VBUS_volts, VBUS_curr, VCONN_volts, VCONN_curr, CC1_volts, CC1_curr, CC2_volts, CC2_curr]
header_dict = {}

with open('export.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')

    for row in readCSV:
        if debug >= 2:
            print(row)

        try:
            if row[0] == 'Time (s)':
                # Identify all the Column Headers
                header_dict = identify_column_headers(row, header_list, debug)

            f = float(row[0])
            if debug >= 2:
                print('Number to covert is {}'.format(f))

            Time_stamp.append(float(row[header_dict['Time (s)']]))
            VBUS_volts.append(float(row[header_dict['VBUS Voltage (V)']]))
            VBUS_curr.append(float(row[header_dict['VBUS Current (A)']]))
            VCONN_volts.append(float(row[header_dict['VCONN Voltage (V)']]))
            VCONN_curr.append(float(row[header_dict['VCONN Current (A)']]))
            CC1_volts.append(float(row[header_dict['CC1 Voltage (V)']]))
            CC1_curr.append(float(row[header_dict['CC1 Current (A)']]))
            CC2_volts.append(float(row[header_dict['CC2 Voltage (V)']]))
            CC2_curr.append(float(row[header_dict['CC2 Current (A)']]))

        except ValueError:
            if debug >= 2:
                print('Skipping row {}'.format(row))


#Slice off last 100 values
VBUS_volts = VBUS_volts[-100:]

for i in range(0, len(data_list)):
    data = data_list[i]
    data_list[i] = data[-100:]
    if debug >= 2:
        print('Data Set: {0}, Data: {1}'.format(data_list[1], data))

#Create Data Dictionary
data_dictionary = dict(zip(header_list, data_list))
print data_dictionary

plot_data(data_dictionary, header_list)

if debug >= 1:
    print('The size of data is {}'.format(len(VBUS_volts)))
    print('VBUS MAX Voltage: {}'.format(max(VBUS_volts)))

    VBUS_volts_std = stdev(VBUS_volts)
    VBUS_volts_ave = ave(VBUS_volts)
