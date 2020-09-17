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
                            help="DC (e.g 'iad1')")
args = parser.parse_args()
site = args.site
username = args.username
password = getpass()
init(autoreset=True)

with open("inventory.yml", "r") as y:
    inventory = yaml.safe_load(y)


def parse_devices():
    now = datetime.now().strftime("%Y-%m-%d %H-%M")
    with open(f"outputs/{site}_{username}", "w") as f:
        f.write(f"Collected at {now}\n\n\n")

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
            print("Collecting config..")
            irb_400 = ssh.send_command("show configuration interfaces irb.400")
            ge_0_2_1_400 = ssh.send_command("show configuration interfaces ge-0/2/1.400")
            ge_0_2_1_0 = ssh.send_command("show configuration interfaces ge-0/2/1.0")
            dhcp_helper = ssh.send_command("show configuration routing-instances CONPOW forwarding-options")

            with open(f"outputs/{site}_{username}", "a") as f:
                f.write(f"\n\n###############\n{host}\n###############\n\n")
                f.write(f"irb.400:\n{irb_400}\n\n")
                f.write(f"ge-0/2/1.400:\n{ge_0_2_1_400}\n\n")
                f.write(f"ge-0/2/1.0:\n{ge_0_2_1_0}\n\n")
                f.write(f"CONPOW dhcp-helper:\n{dhcp_helper}\n\n")
                f.write("*" * 75)
        except Exception as e:
            print(e)
            with open(f"outputs/{site}_{username}", "a") as f:
                f.write(f"\n\n#########\n{host}\n#########\n\n")
                f.write(f"ERROR: {str(e)}")
    print(f"\n\nDone.\nCheck results at outputs/{site}_{username}")
                
if __name__ == '__main__':
    parse_devices()

