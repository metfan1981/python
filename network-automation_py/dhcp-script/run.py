import yaml
import argparse
from getpass import getpass
from jinja2 import Template
from datetime import datetime
from netmiko import ConnectHandler
from colorama import init, Fore, Back, Style


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", dest="username", type=str, required=True,
                            help="Username for network devices")
parser.add_argument("-D", "--deploy", dest="DEPLOY", action="store_true", default=False, 
                            help="Force pushing new config. Disabled by default")
parser.add_argument("-R", "--rollback", dest="ROLLBACK", action="store_true", default=False, 
                            help="Delete dhcp-helper config")                            
args = parser.parse_args()
username = args.username
password = getpass()
init(autoreset=True)
now = datetime.now().strftime("%Y-%m-%d %H-%M")


if args.ROLLBACK:
    jinja_raw_template = "templates/rollback.j2"
    commit_comment = "ROLLBACK-NETENG-2040"
else:
    jinja_raw_template = "templates/config.j2"
    commit_comment = "NETENG-2040"

with open(jinja_raw_template, "r") as j:
    template = Template(j.read())

with open("inventory/dhcp-helper-devices.yml", "r") as y:
    inventory = yaml.safe_load(y)


def configure(interface):
    config = template.render(inventory[interface])
    for device in inventory[interface]["devices"]:
        conn_param = {
            "device_type": "juniper",
            "ip": device,
            "username": username,
            "password": password,
            "verbose": False
        }
        try:
            ssh = ConnectHandler(**conn_param)
            print(f"\nConnected to {device}..")

            # make configuration backup locally at 'backup' dir
            old_relay_cfg = ssh.send_command("show configuration routing-instances CONPOW forwarding-options | display set")
            with open(f"backup/{device}", "a") as f:
                f.write(f"\n\nDATE: {now}")
                f.write(old_relay_cfg)

            if args.DEPLOY:
                ssh.send_config_set(config.splitlines(), exit_config_mode=False, config_mode_command="configure private")
                ssh.commit(comment=commit_comment, and_quit=True)
            else:
                print(Fore.GREEN + Back.WHITE + "Skipping deploy step..")
                print(Fore.GREEN + Back.WHITE + "To force deploy, use '-D' argument")
                print(f"Config for {device} would be:\n{config}")
        except Exception as e:
            print(Fore.RED + Back.WHITE + "Connection error:")
            print(e)


if __name__ == "__main__":
    # repeat 'configure' function for all the inventory devices
    for key in inventory:
        configure(key)
        
    print("Device config backups saved to ./backup")
