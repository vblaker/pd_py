import capture_usbpd
import detect
import timeit
import plot_data
import save_to_csv

# Define headers
iv_type_str = ['Vbus Voltage', 'Vbus Current', 'Vconn Voltage', 'Vconn Current',
    'CC1 Voltage', 'CC1 Current', 'CC2 Voltage', 'CC2 Current']

header_list = ['Time (s)', 'VBUS Voltage (V)', 'VBUS Current (A)', 'VCONN Voltage (V)',
               'VCONN Current (A)', 'CC1 Voltage (V)', 'CC1 Current (A)',
               'CC2 Voltage (V)', 'CC2 Current (A)']

# Set debug and plot flags
debug = 0
plot = 0
save_to_file = 1

# Initialize arrays/lists
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

# Detect PD Analyzers
ports, unique_ids = detect.detect_pd()

# Capture PD Data.
# Sampling is roughly at 8 ms/sample or 125 samples/second. One sample is approximately 8 items on the list
for i in range(len(ports)):
    data = capture_usbpd.capture_usbpd(port=ports[i], mode='iv', num=100, debug=debug)

if debug == 1:
    print (data)

# Parse out data. For time stamp pick every 8th data point
for i in range(len(data)):
    if (i % len(iv_type_str)) == 0:
        Time_stamp.append(data[i][0])
    elif data[i][1] == 'Vbus Voltage':
        VBUS_volts.append(data[i][2])
    elif data[i][1] == 'Vbus Current':
        VBUS_curr.append(data[i][2])
    elif data[i][1] == 'Vconn Voltage':
        VCONN_volts.append(data[i][2])
    elif data[i][1] == 'Vconn Current':
        VCONN_curr.append(data[i][2])
    elif data[i][1] == 'CC1 Voltage':
        CC1_volts.append(data[i][2])
    elif data[i][1] == 'CC1 Current':
        CC1_curr.append(data[i][2])
    elif data[i][1] == 'CC2 Voltage':
        CC2_volts.append(data[i][2])
    elif data[i][1] == 'CC2 Current':
        CC2_curr.append(data[i][2])

# Create Data Dictionary
data_dictionary = dict(zip(header_list, data_list))
if debug == 1:
    print(data_dictionary)

# Iterate through data_dictionary and 0-pad empty lists
for key, value in data_dictionary.items():
    if len(value) == 0:
        data_dictionary[key] = [0.0] * len(data_dictionary['Time (s)'])

    if debug == 1:
        print('Number of samples in {} is {}'.format(key, len(data_dictionary[key])))


# Determine a smallest number of data points on all the lists in dictionary for proper file dump
data_minimum_length = min([len(value) for key, value in data_dictionary.iteritems()])

# Iterate through dictionary to print out data to screen
if debug == 1:
    for i in range(data_minimum_length):
        str_list = []
        j = 0
        h = 0
        for key in data_dictionary:
            header = header_list[h]
            str_list.append(str(data_dictionary[header][j]))
            h += 1
        j += 1

        # Print header only first time
        if i == 0: print(",".join(header_list))
        print(",".join(str_list))

if plot == 1:
    # Call plot function to display IV data
    plot_data.plot_data(data_dictionary)

if save_to_file == 1:
    save_to_csv.save_to_csv(data_dictionary, header_list)
