from netmiko import ConnectHandler
from datetime import datetime
from jinja2 import Template
import yaml

now = datetime.now().strftime("%Y.%m.%d %H-%M")

with open("yml.yml") as y:
    device_info = yaml.safe_load(y)

with open("config.txt") as t:
    template = Template(t.read())

for switch in device_info:
    cisco_ios = {
        "device_type": "cisco_ios",
        "ip": switch,
        "username": "denis",
        "password": "admin",
        "secret": "admin",
        "verbose": False,
        "port": 22
    }

    ssh = ConnectHandler(**cisco_ios)
    print(f"\n\nConnected to {switch}...")
    ssh.enable()

    # config ospf after asking
    config = template.render(device_info.get(switch))
    print(config)
    push_cfg = input("Push this config? <y|n>: ").lower()
    if push_cfg == "y":
        # backup cfg and write to file
        run_cfg_output = ssh.send_command("show run")
        run_cfg_raw = run_cfg_output.splitlines()
        run_cfg = "\n".join(run_cfg_raw[3:-1])
        cfg_file = f"{switch} {now} run-cfg.txt"
        with open(cfg_file, "w") as f:
            f.write(run_cfg)

        # push config
        ssh.send_config_set(config)
        ipint = ssh.send_command_expect("show ip interface brief")
        print(ipint)
        ospf = ssh.send_command_expect("show run | s ospf")
        print(ospf)
        ssh.send_command("wr mem")
        print("Config successfully pushed!")
    else:
        pass

    ssh.disconnect()



