import datetime
import sys
import OS_Detect as osd
import os


def save_to_csv(data_dictionary, header_list):
    os_name, python_version, platform_architecture = osd.os_detect(debug=0)
    home_path = os.path.expanduser('~')

    if os_name == 'Windows':
        path = os.path.join(home_path + "\\TotalPhase\\traces\\")
    elif os_name == 'Linux':
        path = home_path + '/TotalPhase/traces/'

    '''
    # Check if directory exists, and if not then create it
    if not os.path.isdir(path):
        os.mkdir(path)
        print('Folder {} created!'.format(path))
    '''

        # Determine a smallest number of data points on all the lists in dictionary for proper file dump
    data_minimum_length = min([len(value) for key, value in data_dictionary.iteritems()])


    # Write Data to file with name of current date/time
    path = ''       #TODO empty path remove when done debugging
    filename = path + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'

    try:
        with open(filename, 'w') as f:
            # Iterate through dictionary to print out data to screen
            for i in range(data_minimum_length):
                str_list = []
                j = 0
                h = 0
                # for j in range(len(header_list)):
                for key in data_dictionary:
                    header = header_list[h]
                    str_list.append(str(data_dictionary[header][j]))
                    h += 1
                j += 1

                # Print header only first time
                if i == 0: f.write(",".join(header_list) + '\n')
                f.write(",".join(str_list) + '\n')

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    # Close the file when all the data is written
    f.close()
