import csv
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Directory to store individual response files
response_dir = "responses/"
result_file = "results.csv"

# Function to read roll numbers and names from file
def read_rollno_name_file(file_path):
    rollnos_names = {}
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            rollno, name = line.strip().split(",")
            rollnos_names[rollno] = name
    return rollnos_names

@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    return render_template("cancel.html")
# Home route - Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        rollno = request.form["rollno"]
        rollno_names = read_rollno_name_file("rollno_name.txt")
        if rollno in rollno_names:
            name = rollno_names[rollno]
            return redirect(url_for("quiz", rollno=rollno, name=name))
        else:
            return render_template("index.html")
    return render_template("index.html")

# Quiz route - Display quiz questions
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        rollno = request.args.get("rollno")
        name = request.args.get("name")
        responses = []
        marks = 0
        with open("answer1.txt", "r") as f:
            answers = [answer.strip() for answer in f.readlines()]
            for index, answer in enumerate(answers):
                response = request.form.get(f"answer{index}")
                responses.append(response)
                if response == answer:
                    marks += 1
        write_responses_to_file(rollno, responses)
        update_result_file(rollno, name, marks)
        return redirect(url_for("result", name=name, rollno=rollno))
    else:
        rollno = request.args.get("rollno")
        name = request.args.get("name")
        with open("question1.txt", "r") as f:
            questions = [question.strip() for question in f.readlines()]
        with open("custom_options1.txt", "r") as f:
            custom_options = [line.strip().split(",") for line in f.readlines()]
        return render_template("quiz.html", name=name, questions=questions, custom_options=custom_options)

# Function to write responses to individual CSV file
def write_responses_to_file(rollno, responses):
    os.makedirs(response_dir, exist_ok=True)
    file_path = os.path.join(response_dir, f"{rollno}_responses.csv")
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Response"])
        for index, response in enumerate(responses):
            writer.writerow([f"Question {index+1}", response])

# Function to update result file
def update_result_file(rollno, name, marks):
    if os.path.exists(result_file):
        with open(result_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([rollno, name, marks])
    else:
        with open(result_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Roll No", "Name", "Marks"])
            writer.writerow([rollno, name, marks])

# Result route - Display result page
@app.route("/result")
def result():
    name = request.args.get("name")
    rollno = request.args.get("rollno")
    return render_template("result.html", name=name, rollno=rollno)

if __name__ == "__main__":
    app.run(debug=True)
