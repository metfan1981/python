import yaml

with open("yml.yml") as y:
    nice_dict = yaml.safe_load(y)

dict_keys = []
for k in nice_dict:
    dict_keys.append(k)
new_dict_keys = ", ".join(dict_keys)


print("Hello!\nIt is 'nice dictionary app', and we will help you to det rig of bad words!")
print(f"Our dictionary contains these keys: {new_dict_keys}")
usr_input = input(">>> ").lower().split()
new_usr_input = []

for word in usr_input:
    if word in nice_dict.keys():
        new_word = nice_dict.get(word)
        new_usr_input.append(new_word)
    else:
        new_usr_input.append(word)

print(" ".join(new_usr_input))



