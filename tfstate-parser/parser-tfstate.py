import json

# create Ansible inventory "tf-inventory.ini" with [web] group as default
inventory = "tf-inventory.ini"

with open("terraform.tfstate", "r") as j:
    tfstate = json.load(j)
with open(inventory, "w") as f:
    f.writelines("[web]\n")


resource_info = tfstate['resources']
for entries in resource_info:
    if entries['type'] == 'aws_instance':
        for attribute in entries['instances']:
            instance_name = attribute['attributes']['tags']['Name']
            public_ip = attribute['attributes']['public_ip']
            if not public_ip:
                print(f"{instance_name} is private")
                print("___" * 10)
            else:
                print(f"{instance_name}: {public_ip}")
                print("___" *10)
                with open(inventory, "a") as f:
                    f.writelines(f"{instance_name} ansible_host={public_ip}\n")
