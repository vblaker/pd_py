import datetime
import sys
import os


def save_to_csv(data_dictionary, header_list):

    # Determine a smallest number of data points on all the lists in dictionary for proper file dump
    data_minimum_length = min([len(value) for key, value in data_dictionary.iteritems()])

    # Generate OS specific PATH and check if directory exists, and if not then create it
    home_path = os.path.expanduser('~')
    path = os.path.join(home_path, 'TotalPhase', 'traces')
    if not os.path.exists(path):
        os.makedirs(path)

    # Write Data to file with name of current date/time
    filename = os.path.join(path, datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv')

    # Iterate through data_dictionary and write to file one row at a time
    try:
        with open(filename, 'w') as f:
            # Iterate through dictionary to print out data to screen
            for i in range(data_minimum_length):
                str_list = []
                j = 0
                h = 0
                for key in data_dictionary:
                    header = header_list[h]
                    str_list.append(str(data_dictionary[header][j]))
                    h += 1
                j += 1

                if i == 0: f.write(",".join(header_list) + '\n')    # Print header only first time
                f.write(",".join(str_list) + '\n')                  # Write into file

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    f.close()                                                       # Close the file when all the data is written

'''
#######################################
# DEBUGGING ONLY
#######################################
data_dictionary = {'VBUS Voltage (V)': [0.0, 0.0], 'CC2 Current (A)': [0.0, 0.0], 'Time (s)': [0.097629, 0.105629],
                   'VCONN Voltage (V)': [2.395, 2.395], 'VBUS Current (A)': [0.0, 0.0],
                   'VCONN Current (A)': [0.0, 0.0], 'CC1 Current (A)': [0.0, 0.0],
                   'CC2 Voltage (V)': [0.0, 0.0], 'CC1 Voltage (V)': [0.0, 0.0]}

header_list = ['Time (s)', 'VBUS Voltage (V)', 'VBUS Current (A)', 'VCONN Voltage (V)',
               'VCONN Current (A)', 'CC1 Voltage (V)', 'CC1 Current (A)',
               'CC2 Voltage (V)', 'CC2 Current (A)']

save_to_csv(data_dictionary, header_list)
'''