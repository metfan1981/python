#Guess word Game

secret = "cloud"
guess = ""
guess_count = 0
guess_limit = 5
out_of_guesses = False

while guess != secret and not (out_of_guesses):
    if guess_count < guess_limit:
        guess = input("Guess a word: ")
        guess_count += 1
    else:
        out_of_guesses = True

if out_of_guesses:
    print("You lose!")
else:
    print("You win!")
