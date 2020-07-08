class Quiz:
    def __init__(self, type, answer):
        self.type = type
        self.answer = answer

question_pack = [
    "Which color is the sky?\nBlue(b), Red(r), Green(g): ",
    "2+2?\n8, 20, 4: ",
    "Capital of GB?\nManchester(m), London(l), York(y): "
]

exact_q = [
    Quiz(question_pack[0], "b"),
    Quiz(question_pack[1], "4"),
    Quiz(question_pack[2], "l")
]

def quizlet(question_pack):
    count = 0
    for one_q in exact_q:
        answer = input(one_q.type)
        if answer == one_q.answer:
            count += 1
    print("Your score is " + str(count) + " of " + str(len(exact_q)) + " correct!")

quizlet(question_pack)

