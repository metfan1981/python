#!/usr/bin/env python3.6
# by: Denys Korotkyi

import yaml
import argparse
from netmiko import ConnectHandler
from getpass import getpass
from datetime import datetime
from colorama import init, Back, Fore

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", dest="username", type=str, required=True,
                            help="Username for network devices")
parser.add_argument("-s", "--site", dest="site", type=str, required=True,
                            help="DC ('iad1' or 'pdx1')")
args = parser.parse_args()
site = args.site
username = args.username
password = getpass()
init(autoreset=True)


with open("inventory.yml", "r") as y:
    inventory = yaml.safe_load(y)


def parse_devices():
    now = datetime.now().strftime("%Y-%m-%d %H-%M")
    with open(f"outputs/{site}", "w") as f:
        f.write(f"Collected at {now}")

    for host in inventory[site]:
        device = {
            "device_type": "juniper",
            "ip": host,
            "username": username,
            "password": password,
            "verbose": False
        }

        print(Fore.GREEN + Back.WHITE + f"{host}..")
        try:
            ssh = ConnectHandler(**device)
            interfaces = ssh.send_command('show configuration interfaces | display set | match "description|inet"')
            lldp = ssh.send_command('show lldp neighbors')
            with open(f"outputs/{site}", "a") as f:
                f.write(f"\n\n{host}\n\n")
                f.write(f"{interfaces}\n\n")
                f.write(f"LLDP:\n{lldp}\n\n")
        except Exception as e:
            print(e)
            with open(f"outputs/{site}_errors", "a") as f:
                f.write(f"\n\n{host}\n\n")
                f.write(f"ERROR: {str(e)}")

                
if __name__ == '__main__':
    parse_devices()
