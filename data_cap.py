import capture_usbpd
import detect
import timeit
import plot_data
import save_to_csv

# Define headers
iv_type_str = ['Vbus Voltage', 'Vbus Current', 'Vconn Voltage', 'Vconn Current',
    'CC1 Voltage', 'CC1 Current', 'CC2 Voltage', 'CC2 Current']

header_list = ['Time', 'Vbus Voltage', 'Vbus Current', 'Vconn Voltage', 'Vconn Current',
    'CC1 Voltage', 'CC1 Current', 'CC2 Voltage', 'CC2 Current', 'Real-Time Stamp']

# Set column positions for data labels and data values
col_data_label = 1
col_data_val = 2


# Set debug and plot flags
debug = 0
plot = 0
save_to_file = 1
sampling_time_ms = 5000
num_samples = ((sampling_time_ms + 300) / 1000 * 125)

# Detect PD Analyzers
ports, unique_ids = detect.detect_pd()

# Capture PD Data. Sampling is roughly at 8 ms/sample or 125 samples/second.
for i in range(len(ports)):
    data = capture_usbpd.capture_usbpd(port=ports[i], mode='iv', num=num_samples, debug=debug)

if debug == 1:
    print (data)


header_dictionary = dict(zip(header_list, range(len(header_list))))     # Create header dictionary
data_dictionary = {key: [] for key in header_dictionary}                # Init data dictionary

if debug == 1:
    print(data_dictionary)

# Parse out data and assign real-time labels to samples
#  time_stamp = datetime.datetime.strptime('2017-10-10 12:05:48.442000', '%Y-%m-%d %H:%M:%S.%f') TODO
#  time_stamp + datetime.timedelta(seconds=120) TODO

for i in range(len(data)):
    for j in range(len(iv_type_str)):
        if data[i][col_data_label] == iv_type_str[j]: data_dictionary[(iv_type_str[j])].append(data[i][col_data_val])
        else: data_dictionary[(iv_type_str[j])].append('-')

    data_dictionary['Time'].append(data[i][0])
    data_dictionary['Real-Time Stamp'].append(data[i][3])

# Determine a largest number of data points on all the lists in dictionary for proper file dump
data_min_length = min([len(value) for key, value in data_dictionary.iteritems()])

# Iterate through dictionary to print out data to screen
if debug == 1:
    for i in range(data_min_length):
        str_list = []
        j = 0
        h = 0
        for key in data_dictionary:
            header = header_list[h]
            str_list.append(str(data_dictionary[header][i]))
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
