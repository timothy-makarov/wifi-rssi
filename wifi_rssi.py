#
# Microsoft Windows use only!
# Depends on netsh command line utility.
# Signal quality to RSSI conversion see below:
# https://stackoverflow.com/questions/15797920/how-to-convert-wifi-signal-strength-from-quality-percent-to-rssi-dbm
#


import re
import subprocess
import sys
import time

from datetime import datetime


ENCODING = "866"


def query_interfaces():
    query = subprocess.check_output("netsh wlan show all",
                                    shell=True,
                                    text=True,
                                    encoding=ENCODING)
    return query


def parse_wifi_params(query):
    wlans = map(lambda x: x[0],
                re.findall("(^SSID(.|\n)+?(?=\n^\n))+?",
                           query,
                           flags=re.MULTILINE))
    wxs = []
    for wlan in wlans:
        lines = wlan.split("\n")
        wx = {}
        for idx in range(len(lines)):
            line = lines[idx]
            line = line.strip()
            if (line.startswith("SSID")):
                line = re.sub("SSID\s\d+\:\s?", "", line)
                if (len(line) == 0):
                    continue
                wx["ssid"] = line
            elif (line.startswith("BSSID")):
                line = re.sub("BSSID\s\d+\:\s?", "", line)
                wx["bssid"] = line.strip()
                line = lines[idx + 1]
                line = re.search("\d+(?=%)", line).group(0)
                wx["quality"] = float(line)
                wx["rssi"] = wx["quality"] / 2 - 100
                continue
            else:
                continue
        if ("ssid" in wx):
            wxs.append(wx)
    return wxs


def format_table_header():
    print("Timestamp;SSID;BSSID;Quality;RSSI")


def format_table_row(timestamp, rows):
    for row in rows:
        print("{};{};{};{};{}".format(
            timestamp,
            row["ssid"],
            row["bssid"],
            row["quality"],
            row["rssi"]
        ))


def main(argv):
    format_table_header()
    while True:
        timestamp = datetime.now()
        query = query_interfaces()
        wxs = parse_wifi_params(query)
        format_table_row(timestamp, wxs)
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv)
