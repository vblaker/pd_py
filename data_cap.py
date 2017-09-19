import capture_usbpd
import detect

ports, unique_ids = detect.detect_pd()

#num = int(input('Number of samples to acquire: ')) * 6

for i in range(len(ports)):
    data = capture_usbpd.capture_usbpd(port=ports[i], mode='iv', num=5)
    print (data)