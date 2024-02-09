#!/usr/bin/env python3
import sys
import json
import itertools
import time
from openai import OpenAI
import threading
import random
import ast
import os
import fitz
import tiktoken
import requests
import click

base_dir = __file__

base_dir = base_dir[:len(base_dir)-8]

print(base_dir)

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

class QuizCreationError(Exception):
    def message(self):
        return "Quiz creation did not pass validation checks. Please try again."

def argument_checker(user_input, allowed_inputs=None, numerical=False, true_false=False, answers=None):
    while True:
        if allowed_inputs:
            user = input(user_input)
            if user.lower() in allowed_inputs:
                if true_false:
                    index = allowed_inputs.index(user)
                    t_f = True if index == 0 else False
                    if t_f:
                        if t_f in answers:
                            print("There is already an answer that's 'true'")
                        else:
                            return t_f
                    else:
                        return t_f
                else:
                    return user
            else:
                print(f"Please input one of these arguments: {', '.join([i for i in allowed_inputs])}")
        elif numerical:
            user = input(user_input)
            if not user.isdigit():
                print("Please input a valid number")
            else:
                return int(user)




def loading_spinner(stop_event):
    print("Building Quiz")
    spinner = itertools.cycle(["-", "/", "|", "\\"])
    while not stop_event.is_set():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')

def running_quiz(quiz):
    questions = quiz['questions']
    print("Exit quiz by typing CTRL C")
    while True:
        for question_idx in range(len(questions)):
            print("\n" + questions[question_idx]['question'])
            valid_inputs = []
            answer = None
            shuffled_answers = questions[question_idx]['answers']
            random.shuffle(shuffled_answers)
            for idx in range(len(questions[question_idx]['answers'])):
                key = list(shuffled_answers[idx].keys())[0]
                value = list(shuffled_answers[idx].values())[0]
                valid_inputs.append(alphabet[idx].lower())
                print(f"{alphabet[idx]} - {key}")
                if value:
                    answer = alphabet[idx]
            user = argument_checker("Answer: ", valid_inputs)
            if user == answer.lower():
                print("\nCorrect!")
            else:
                print("\nIncorrect :(")
                print(f"Correct Answer: {answer}")
                wrong_question = questions.pop(question_idx)
                if (len(questions) - question_idx) >= 3:
                    questions.insert(question_idx+3, wrong_question)
                elif (len(questions) - question_idx) == 2:
                    questions.insert(0, wrong_question)
                elif (len(questions) - question_idx) == 1:
                    questions.insert(1, wrong_question)
                else:
                    questions.insert(2, wrong_question)


def is_valid_directory(prompt):
    while True:
        user = input(prompt)
        if os.path.exists(user):

            return user
        else:
            print(f"{user} does not exist.")

def check_quality(quiz):
    try:
        for inquiz in quiz['questions']:

            for answers in inquiz['answers']:
                for key, value in answers.items():
                    if value not in [True, False]:
                        raise ValueError
            x = inquiz["question"]
    except:
        return False

    return quiz


def scrapePDF(pdf_path):
    enc = tiktoken.get_encoding("cl100k_base")
    text = ""
    doc = fitz.open(pdf_path)
    token_total = 0
    for page_num in range(doc.page_count):
        page = doc[page_num]
        token_amount = enc.encode(page.get_text())
        token_total += len(token_amount)
        print(token_total)
        if token_total > 5000:
            doc.close()
            return text
        else:
            text += page.get_text()

    doc.close()
    print(text)
    return text



def generate(api_key, num_questions, facts):
    client = OpenAI(api_key=api_key)
    example = {'questions': [{'question': 'How many countries are in the world?', 'answers':
        [{'195 countries': True}, {'125 countries': False}, {'45 countries': False}, {'32 countries': False}]}]}

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": f"You are a quiz creator. Please create "
                                          f"{num_questions} hard quiz questions about the following lecture slides. Make sure to ONLY respond in Python DICTIONARY format "
                                          f"STRICTLY following the example below: "
                                          f"eg {example}"},
            {"role": "user", "content": f"Lecture slides: {facts}"},
        ],
        max_tokens=10000,
        temperature=0
    )
    return response.choices[0].message.content

def help():
    print("""                                                                
       ___  _   _ ___ __________
      / _ \| | | |_ _|__  /__  /
     | | | | | | || |  / /  / / 
     | |_| | |_| || | / /_ / /_ 
      \__\_\\___/|___/____/____|
                                """)
    print("Quiz creator for the command line")
    print("Options:")
    print("-nq, --new-quiz      Create a new quiz")
    print("-pq, --prev-quiz     Use an previous quiz")
    print("-del, --delete       Delete previous quiz")
    print("-pd, --pub-quiz      Access public quiz database")
    print("-pub, --publish       Publish your personal quiz to the public database")
    print("-h, --help           Documentation")
    print("CTRL C to exit")



def main():
    if len(sys.argv) <= 1:
        help()

    else:
        try:
            if sys.argv[1] == '--new-quiz' or sys.argv[1] == '-nq':
                quiz_name = input("Quiz Name: ")
                ai = argument_checker("Generate questions with AI? y/n: ", ['y', 'n'])
                if ai == 'y':
                    with open(f"{base_dir}/database/data.json", "r") as database:
                        data = json.load(database)
                        if data['api_key'] == "":
                            api_key = input("Please enter OpenAI API key: ")
                            data['api_key'] = api_key
                            with open(f'{base_dir}/database/data.json', "w") as database:
                                json.dump(data, database)
                        else:
                            source = is_valid_directory("Directory eg: ./lectures/CSIT123.pdf: ")
                            text = scrapePDF(source)
                            while True:
                                num_questions = argument_checker("How many questions?: ", numerical=True)
                                api_key = data['api_key']
                                stop_event = threading.Event()
                                spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event,))
                                spinner_thread.start()

                                quiz = generate(api_key, num_questions, text)
                                try:
                                    quiz = ast.literal_eval(quiz)
                                    quiz = check_quality(quiz)
                                    if not quiz:
                                        raise QuizCreationError
                                    stop_event.set()
                                    spinner_thread.join()
                                    print("Done")
                                    break
                                except SyntaxError:
                                    print("Unfortunately we have run out of context.\nPlease choose a smaller amount of questions")
                                    stop_event.set()
                                    spinner_thread.join()
                                    sys.exit(0)

                                except QuizCreationError:
                                    print(QuizCreationError().message())
                                    sys.exit(0)

                            new_quiz = {'quiz_name': quiz_name, 'quiz': quiz}
                            with open(f"{base_dir}/database/data.json", "r") as database:
                                data = json.load(database)
                                data['quizzes'].append(new_quiz)
                                with open(f"{base_dir}/database/data.json", "w") as database:
                                    json.dump(data, database)

                            running_quiz(quiz)
                else:

                    new_quiz = {"quiz_name": quiz_name, "quiz": {'questions': []}}

                    mc_count = argument_checker("How many answers per question?: ", numerical=True)
                    print("If you would like to stop adding questions enter: quit")
                    counter = 0
                    while True:
                        counter += 1
                        user = input(f"Question {counter}: ")
                        if user.lower() == "quit":
                            check = check_quality(new_quiz['quiz'])
                            print("failed") if not check else print("success")
                            break
                        quiz_question = {'question': user, 'answers': []}
                        answers = []
                        for i in range(mc_count):
                            answer = input(f"Answer {i+1}: ")
                            t_f = argument_checker("True/False? t/f: ", ['t', 'f'], true_false=True, answers=answers)
                            answers.append(t_f)
                            quiz_question['answers'].append({answer: t_f})
                        new_quiz['quiz']['questions'].append(quiz_question)

                    with open(f"{base_dir}/database/data.json", "r") as database:
                        data = json.load(database)
                        data['quizzes'].append(new_quiz)
                        with open(f"{base_dir}/database/data.json", "w") as database:
                            json.dump(data, database)

            elif sys.argv[1] == "-pq" or sys.argv[1] == "--prev-quiz":
                with open(f"{base_dir}/database/data.json", "r") as database:
                    data = json.load(database)
                    if len(data['quizzes']) > 0:
                        for idx, quiz in enumerate(data['quizzes']):
                            print(f"{idx+1} - {quiz['quiz_name']}")

                        user = argument_checker("Enter the quiz code: ",
                                                allowed_inputs=[str(i+1) for i in range(len(data['quizzes']))])
                        quiz = data['quizzes'][int(user)-1]['quiz']

                        running_quiz(quiz)

                    else:
                        print("No quizzes yet!")



            elif sys.argv[1] == "-del" or sys.argv[1] == "--delete":
                with open(f"{base_dir}/database/data.json", "r") as database:
                    data = json.load(database)
                    if len(data['quizzes']) > 0:
                        for idx, quiz in enumerate(data['quizzes']):
                            print(f"{idx+1} - {quiz['quiz_name']}")
                        user = argument_checker("Enter the quiz code to delete: ",
                                                    allowed_inputs=[str(i + 1) for i in range(len(data['quizzes']))])
                        del data['quizzes'][int(user)-1]
                        with open(f"{base_dir}/database/data.json", "w") as database:
                            json.dump(data, database)
                        print("Deleted")
                    else:
                        print("No quizzes yet!")

            elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
                help()

            elif sys.argv[1] == "-pd" or sys.argv[1] == "--pub-quiz":
                with requests.get("http://194.195.124.19:5050/quizzes") as response:
                    if response.status_code == 200:
                        data = response.json()
                    else:
                        print("Network error")
                        sys.exit(0)


                if len(data['quizzes']) > 0:
                    for idx, quiz in enumerate(data['quizzes']):
                        print(f"{idx + 1} - {quiz['quiz_name']}")

                    user = argument_checker("Enter the quiz code: ",
                                            allowed_inputs=[str(i + 1) for i in range(len(data['quizzes']))])
                    quiz = data['quizzes'][int(user) - 1]['quiz']

                    running_quiz(quiz)

                else:
                    print("No quizzes yet!")

            elif sys.argv[1] == "-pub" or sys.argv[1] == "--publish":
                with open(f"{base_dir}/database/data.json", "r") as database:
                    data = json.load(database)
                    if len(data['quizzes']) > 0:
                        for idx, quiz in enumerate(data['quizzes']):
                            print(f"{idx + 1} - {quiz['quiz_name']}")
                        user = argument_checker("Enter the quiz code to publish: ",
                                                allowed_inputs=[str(i + 1) for i in range(len(data['quizzes']))])
                        chosen_quiz = data['quizzes'][int(user) - 1]

                        with requests.post("http://194.195.124.19:5050/add-quiz", json=chosen_quiz) as response:
                            print(response.json()["message"])
                    else:
                        print("No quizzes yet!")


        except KeyboardInterrupt:
            print("\nGoodbye :)\n")
            sys.exit(0)

if __name__ == "__main__":
  main()



