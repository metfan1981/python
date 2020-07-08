import datetime
from netmiko import Netmiko
from netmiko import ConnectHandler
from getpass import getpass

username = input("Username: ")
password = getpass()

# don't forget to create 'devices.txt' in same directory
# and write devices IP addresses line by line
with open("devices.txt") as f:
    devices = f.read().splitlines()

for device in devices:
    cisco_device = {
        "device_type": "cisco_ios",
        "ip": device,
        "username": username,
        "password": password,
        "port": 22,
        "secret": password,
        "verbose": True,
    }

    ssh = ConnectHandler(**cisco_device)
    ssh.enable()
    prompt = ssh.find_prompt()

    print(f"Saving cfg of {device}...")

    # reformatting output of ‘sh run’ to save only that lines we can paste into CLI
    run_cfg_raw = ssh.send_command_expect("show running-config")
    run_cfg_raw_list = run_cfg_raw.split("\n")
    run_cfg = "\n".join(run_cfg_raw_list[3:-1])

    now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")
    cfg_file = f"C:\\Users\\dkorotk\\PycharmProjects\\Giraffe\\{prompt[:-1]} {now}.txt "
    print(f"Writing config to {cfg_file}...")
    with open(cfg_file, "w") as f:
        f.write(run_cfg)

    print("Done!\n\n")
    ssh.disconnect()

print("Finished for all devices.")
