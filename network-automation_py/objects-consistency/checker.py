import yaml
import argparse
from netmiko import ConnectHandler
from getpass import getpass
from os import popen
from colorama import init, Back, Fore

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", dest="username", type=str, required=True,
                    help="Username for ASA")
parser.add_argument("-s", "--site", dest="site", type=str, required=True,
                    help="DC (e.g 'scs2')")
parser.add_argument("-p", "--pool", dest="pool", type=str, required=True,
                    help="Pool ID (e.g for object-group rpool-10201 POOL ID is '10201')")
args = parser.parse_args()
dc = args.site
pool = args.pool
username = args.username
password = getpass()
init(autoreset=True)

with open("/home/netops/migration_ASA_NAT/consistency_check/device_info.yml") as y:
    device_info = yaml.safe_load(y)

switches = [
    f"sw-core-01-{dc}-scansafe.{dc}",
    f"sw-core-02-{dc}-scansafe.{dc}"
]


def fw_pairs_count():
    if device_info["pairs_count"][dc] == 1:
        fw_list = [f"fw-brd-01-{dc}-scansafe.{dc}"]
    elif device_info["pairs_count"][dc] == 2:
        fw_list = [
            f"fw-brd-01-{dc}-scansafe.{dc}",
            f"fw-brd-03-{dc}-scansafe.{dc}"
        ]
    elif device_info["pairs_count"][dc] == 3:
        fw_list = [
            f"fw-brd-01-{dc}-scansafe.{dc}",
            f"fw-brd-03-{dc}-scansafe.{dc}",
            f"fw-brd-05-{dc}-scansafe.{dc}"
        ]
    return fw_list


sw_core = {}
def sw_check(host):
    device = {
        "device_type": "cisco_nxos",
        "ip": host,
        "username": username,
        "password": password,
        "secret": password,
        "port": 22,
        "verbose": False
    }
    ssh = ConnectHandler(**device)
    print(Fore.YELLOW + f"Checking {host}..")
    raw_objects = ssh.send_command(f"show object-group {dc}-rpool-{pool}")
    objects_list = []
    for line in raw_objects.split("\n"):
        if "host" in line:
            objects_list.append(line.split()[-1])
    sw_core.update({host: objects_list})
    ssh.disconnect()


fw = {}
def asa_check(host):
    device = {
        "device_type": "cisco_asa",
        "ip": host,
        "username": username,
        "password": password,
        "secret": password,
        "port": 22,
        "verbose": False
    }
    ssh = ConnectHandler(**device)
    ssh.enable()
    print(Fore.YELLOW + f"Checking {host}..")
    asa_object_group = ssh.send_command(f"show run object-group id rpool-{pool}")
    mps_objects, objects_list = [], []
    for line in asa_object_group.split("\n"):
        if "network-object" in line:
            mps_objects.append(line.split()[-1])
    for object in mps_objects:
        single_object = ssh.send_command(f"show run object id {object}")
        for line in single_object.split("\n"):
            if "host" in line:
                objects_list.append(line.split()[-1])
        fw.update({host: objects_list})
    ssh.disconnect()


result = {}
def main():
    # pull objects from both switches
    for switch in switches:
        sw_check(switch)
    # between switches
    sw_1 = sorted(sw_core[switches[0]])
    sw_2 = sorted(sw_core[switches[1]])
    if sw_1 == sw_2:
        print(Fore.GREEN + Back.WHITE + "Between switches: OK")
        switch_consistent = True
    else:
        print(Fore.RED + "Between switches: Inconsistent!")
        switch_consistent = False
        for ip in sw_1:
            if ip not in sw_2:
                print(Fore.RED + f"sw-core-01 {ip} isn't present in sw-core-02 config!")
        for ip in sw_2:
            if ip not in sw_1:
                print(Fore.RED + f"sw-core-02 {ip} isn't present in sw-core-01 config!")
    # pull objects from all fw-pairs
    for pair in fw_pairs_count():
        asa_check(pair)
    # between fw-pairs
    fw_1 = sorted(fw[fw_pairs_count()[0]])
    if len(fw_pairs_count()) == 3:
        fw_2 = sorted(fw[fw_pairs_count()[1]])
        fw_3 = sorted(fw[fw_pairs_count()[2]])
        if fw_1 == fw_2 and fw_1 == fw_3 and fw_2 == fw_3:
            print(Fore.GREEN + Back.WHITE + "Between firewalls: OK")
            fw_consistent = True
        else:
            print(Fore.RED + "Between firewalls: Inconsistent!")
            fw_consistent = False
    elif len(fw_pairs_count()) == 2:
        fw_2 = sorted(fw[fw_pairs_count()[1]])
        if fw_1 == fw_2:
            print(Fore.GREEN + Back.WHITE + "Between firewalls: OK")
            fw_consistent = True
        else:
            print(Fore.RED + "Between firewalls: Inconsistent!")
            fw_consistent = False
    # write collected configs to yaml
    result.update({"SW-CORE": sw_core})
    result.update({"ASA": fw})
    file = f"/home/netops/migration_ASA_NAT/consistency_check/results/{pool}_cfg.yml"
    with open(file, "w") as y:
        yaml.dump(result, y)
    # between switch-01 and fw-01
    if switch_consistent and fw_consistent:
        if sw_1 == fw_1:
            print(Fore.RED + "\nConfigs are identical between sw-core-01 and fw-brd-01\nVIP host missing in sw-core-01 object-group.\n")
        else:
            print(Fore.YELLOW + "\nChecking differences between sw-core-01 and fw-brd-01...")
            for ip in sw_1:
                if ip not in fw_1:
                    print(Fore.YELLOW + f"SW-CORE's '{ip}' not present in ASA config.")
            for ip in fw_1:
                if ip not in sw_1:
                    print(Fore.YELLOW + f"ASA's '{ip}' not present in SW-CORE config.")
            if len(sw_1) - 1 == len(fw_1):
                print(Fore.GREEN + Back.WHITE + f"\nOnly 1 IP more in sw-core configuration\nMust be VIP of Pool {pool}.\n\nChecks SUCCEED")
    else:
        print(Fore.RED + "\nCannot compare switches and firewalls. Consistency Error occurred:")
        if not switch_consistent and not fw_consistent:
            print(Fore.RED + "Both switches and firewalls configs (sw <-> sw or fw <-> fw) are incompatible with each other")
        elif not switch_consistent:
            print(Fore.RED + "sw-core-01 <-> sw-core-02 configs are different")
        elif not fw_consistent:
            print(Fore.RED + "Firewall configs are incompatible with each other")
    answer = input("Show results file? <y|n>: ").lower()
    if answer == "y":
        popen(f"cat {file}")


if __name__ == '__main__':
    main()
