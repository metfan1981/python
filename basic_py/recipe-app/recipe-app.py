import json

# ingredients values
with open("js.json", "r") as j:
    recipes = json.load(j)


# print recipe (inserting 'name' of dictionary typed by user)
def ingredients_print():
    print("=" * 25)
    print(f"{answer.capitalize()} recipe:")
    print("=" * 25)
    recipe_print()
    print("=" * 25)



# Calculate new recipe values
def ingredients_calculation():
    residue = recipes.get(answer.capitalize()).get(missing_ingr.capitalize()) / missing_ingr_amount
    for key in recipes.get(answer.capitalize()).keys():
        new_value = recipes.get(answer.capitalize()).get(key) / residue
        recipes.get(answer.capitalize()).update({key: new_value})
    print("=" * 25)
    print("New recipe:")
    print("=" * 25)
    recipe_print()
    print("=" * 25)


# Whole recipe printing
def recipe_print():
    for key in recipes.get(answer.capitalize()).keys():
        print(f"{key}: {round(recipes.get(answer.capitalize()).get(key))}")


answer = input("What do you want to cook?\n=========================\nOmelette\Cake\Easter cake: ").lower()
if answer == "easter cake":
    print("Note: recipe for 3 portions")
ingredients_print()
missing_ingr = input("Specify which ingredient you have insufficient: ").capitalize()
missing_ingr_amount = float(input(f"How much of {missing_ingr} you have now: "))


ingredients_calculation()

calc_prompt = input("Use 'grams => teaspoon converter'?\n<y|n>: ").lower()
while calc_prompt == "y":
    gram = float(input("Enter 'grams' value: "))
    teasp = gram / 4.260
    tabsp = gram / 15
    print(f"{gram} grams is {round(teasp)} teaspoons (or {round(tabsp)} tablespoon)")
    exit_prompt = input("Press 'E' to exit or any key to continue:" ).lower()
    if exit_prompt == "e":
        break
    else:
        continue


input("\n\nPress Enter to exit: ")

