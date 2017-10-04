import os
from subprocess import check_output, CalledProcessError

try:
    adb_output = check_output(["adb", "devices"])
    adb_str_list = (adb_output.split('\r\n'))
    adb_output = check_output(["adb", "root"])
    print(adb_str_list)
    print(adb_str_list[1].split('\t'))
    print(adb_output)
    os.system("adb root")
    os.system("adb pull /data/power_supply_logger/power_supply_info.csv .")

except CalledProcessError as e:
    print(e.returncode)
    print(e)
