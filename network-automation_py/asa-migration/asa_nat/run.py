import yaml
import argparse
from jinja2 import Template
from netmiko import ConnectHandler
from getpass import getpass
from datetime import datetime
from tabulate import tabulate
from colorama import init, Fore, Back, Style


parser = argparse.ArgumentParser()
parser.add_argument("-D", "--deploy", dest="DEPLOY", action="store_true", default=False, help="Use to push new config (<Y|n> will be asked)")
args = parser.parse_args()

with open("./task/task.yml") as y:
    task = yaml.safe_load(y)
with open("./templates/device_info.yml") as y:
    device_info = yaml.safe_load(y)

init(autoreset=True)
username = input("Username for ASA: ")
password = getpass()


def fw_pairs_count(dict_arg):
    dc = dict_arg['dst_dc']
    if device_info["pairs_count"][dc] == 1:
        pairs = [f"fw-brd-01-{dc}-scansafe.{dc}"]
    elif device_info["pairs_count"][dc] == 2:
        pairs = [
            f"fw-brd-01-{dc}-scansafe.{dc}",
            f"fw-brd-03-{dc}-scansafe.{dc}"
        ]
    elif device_info["pairs_count"][dc] == 3:
        pairs = [
            f"fw-brd-01-{dc}-scansafe.{dc}",
            f"fw-brd-03-{dc}-scansafe.{dc}",
            f"fw-brd-05-{dc}-scansafe.{dc}"
        ]
    return pairs


def pair_primary(dict_arg):
    dc = dict_arg['dst_dc']
    if dc in device_info['mngt']:
        pair_primary = None
    else:
        pair_primary = fw_pairs_count(dict_arg)[dict_arg['primary_pair'] - 1]
    return pair_primary


def ip_builder(arg):
    ip = arg.split(" ")[-1]
    return ip.strip()


def cfg_backup(device, command):
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file = f"./backups/{device}-{now}.txt"
    with open(file, "w") as f:
        f.write(command)


result_before = [["DEVICE", "NEW CFG", "POOL"]]
result_after = [["DEVICE", "OLD CFG", "NEW CFG", "POOL"]]
def result_table(table):
    print(tabulate(table, headers="firstrow", tablefmt="grid"))


main_cfg, ctr_cfg = {}, {}
def pull_cfg(dict_arg, *args):
    dc = dict_arg['src_dc']
    pool = dict_arg['src_pool']
    tun_asa = f"fw-brd-01-{dc}-tunnelling.{dc}"
    ss_asa = f"fw-brd-01-{dc}-scansafe.{dc}"
    device = {
        "device_type": "cisco_asa",
        "username": username,
        "password": password,
        "secret": password,
        "port": 22,
        "verbose": False
    }
    if args:
        device.update({"ip": tun_asa})
        ssh = ConnectHandler(**device)
        ssh.enable()
        ctr = ssh.send_command(f"show run object id ctr.access{pool}-nat")
        ctr_cfg.update({f"{pool}_ctr": ip_builder(ctr)})
    else:
        device.update({"ip": ss_asa})
        ssh = ConnectHandler(**device)
        ssh.enable()
        access = ssh.send_command(f"show run object id access{pool}-nat")
        egress = ssh.send_command_expect(f"show run object id egress{pool}")
        main_cfg.update({f"{pool}_access": ip_builder(access)})
        main_cfg.update({f"{pool}_egress": ip_builder(egress)})
    ssh.disconnect()


def cfg_builder(dict_arg, *args):
    tun_asa = f"fw-brd-01-{dict_arg['dst_dc']}-tunnelling.{dict_arg['dst_dc']}"
    dst_pool = dict_arg['dst_pool']
    src_pool = dict_arg['src_pool']
    if args:
        with open("./templates/ctr-config.txt") as f:
            template = Template(f.read())
        cfg_set = template.render(pool=dst_pool,
                                  ctr_ingress=ctr_cfg[f"{src_pool}_ctr"])
        result_before.append([tun_asa, cfg_set, dst_pool])
    else:
        for pair in fw_pairs_count(dict_arg):
            if pair == pair_primary(dict_arg):
                with open("./templates/primary-config.txt") as f:
                    template = Template(f.read())
                cfg_set = template.render(pool=dst_pool,
                                          ingress=main_cfg[f"{src_pool}_access"],
                                          egress=main_cfg[f"{src_pool}_egress"])
                result_before.append([pair, cfg_set, dst_pool])
            elif pair != pair_primary(dict_arg):
                with open("./templates/secondary-config.txt") as f:
                    template = Template(f.read())
                cfg_set = template.render(pool=dst_pool,
                                          ingress=main_cfg[f"{src_pool}_access"],
                                          egress=main_cfg[f"{src_pool}_egress"])
                result_before.append([pair, cfg_set, dst_pool])


def main(dict_arg, *args):
    dst_pool = dict_arg['dst_pool']
    src_pool = dict_arg['src_pool']
    tun_asa = f"fw-brd-01-{dict_arg['dst_dc']}-tunnelling.{dict_arg['dst_dc']}"
    device = {
        "device_type": "cisco_asa",
        "username": username,
        "password": password,
        "secret": password,
        "port": 22,
        "verbose": False
    }
    if args:
        device.update({"ip": tun_asa})
        ssh = ConnectHandler(**device)
        ssh.enable()
        ctr = ssh.send_command(f"show run object id ctr.access{dst_pool}-nat")
        if "ERROR" in ctr:
            ctr = f"\n*** No preconfigured object\n        for CTR Pool {dst_pool} ***\n"
        with open("./templates/ctr-config.txt") as f:
            template = Template(f.read())
        cfg_set = template.render(pool=dst_pool,
                                  ctr_ingress=ctr_cfg[f"{src_pool}_ctr"])
        result_after.append([tun_asa, ctr, cfg_set, dst_pool])
        run_cfg = ssh.send_command("show runn")
        cfg_backup(tun_asa, run_cfg)
        ssh.send_config_set(cfg_set)
        ssh.send_command_expect("wr mem")
        ssh.disconnect()
    else:
        for pair in fw_pairs_count(dict_arg):
            device.update({"ip": pair})
            ssh = ConnectHandler(**device)
            ssh.enable()
            access = ssh.send_command(f"show run object id access{dst_pool}-nat")
            egress = ssh.send_command_expect(f"show run object id egress{dst_pool}")
            if "ERROR" in access:
                access = f"\n*** No preconfigured access object\n         for Pool {dst_pool} ***\n"
            if "ERROR" in egress:
                egress = f"\n*** No preconfigured egress object\n         for Pool {dst_pool} ***\n"
            if pair == pair_primary(dict_arg):
                with open("./templates/primary-config.txt") as f:
                    template = Template(f.read())
                cfg_set = template.render(pool=dst_pool,
                                          ingress=main_cfg[f"{src_pool}_access"],
                                          egress=main_cfg[f"{src_pool}_egress"])
            elif pair != pair_primary(dict_arg):
                with open("./templates/secondary-config.txt") as f:
                    template = Template(f.read())
                cfg_set = template.render(pool=dst_pool,
                                          ingress=main_cfg[f"{src_pool}_access"],
                                          egress=main_cfg[f"{src_pool}_egress"])
            result_after.append([pair, access + egress, cfg_set, dst_pool])
            run_cfg = ssh.send_command("show runn")
            cfg_backup(pair, run_cfg)
            ssh.send_config_set(cfg_set)
            ssh.send_command_expect("wr mem")
            ssh.disconnect()


if __name__ == '__main__':
    print(Fore.GREEN + Back.WHITE + "\nPulling old configurations..")
    for action in task:
        pull_cfg(action)
        if action["ctr_enabled"]:
            pull_cfg(action, "CTR")
    print(Fore.GREEN + Back.WHITE + "Generating new configurations..")
    for action in task:
        cfg_builder(action)
        if action["ctr_enabled"]:
            cfg_builder(action, "CTR")
    result_table(result_before)
    if args.DEPLOY:
        answer = input(Fore.YELLOW + "\n\nPush new config? <Y|n>: ")
        if answer == "Y":
            print(Fore.GREEN + Back.WHITE + "\nDeploying.\nPlease wait, it may take a while..")
            for action in task:
                main(action)
                if action["ctr_enabled"]:
                    main(action, "CTR")
            print(Fore.GREEN + Back.WHITE + "\nSucceed.\nConfigs backup saved to './backups'.\nChanges made:\n")
            result_table(result_after)

