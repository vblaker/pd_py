import capture_usbpd
import detect
import timeit
import plot_data

# Define headers
iv_type_str = ['Vbus Voltage', 'Vbus Current', 'Vconn Voltage', 'Vconn Current',
    'CC1 Voltage', 'CC1 Current', 'CC2 Voltage', 'CC2 Current']

header_list = ['Time (s)', 'VBUS Voltage (V)', 'VBUS Current (A)', 'VCONN Voltage (V)',
               'VCONN Current (A)', 'CC1 Voltage (V)', 'CC1 Current (A)',
               'CC2 Voltage (V)', 'CC2 Current (A)']

# Set debug and plot flags
debug = 0
plot = 1

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
    data = capture_usbpd.capture_usbpd(port=ports[i], mode='iv', num=625, debug=debug)

if debug == 1:
    print (data)


# Parse out data
for i in range(len(data)):
    if (i % 8) == 0:
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
    print('Number of VBUS_voltage samples is {}'.format(len(VBUS_volts)))
    print('Number of Time Samples is {}'.format(len(Time_stamp)))

if plot == 1:
    # Call plot function to display IV data
    plot_data.plot_data(data_dictionary)

