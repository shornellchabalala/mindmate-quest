from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import json, os, random
import google.generativeai as genai # type: ignore

app = Flask(__name__)
app.secret_key = "super-secret-key"

# ==== CONFIG ====
DATA_FILE = "data.json"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ==== DATA HELPERS ====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "xp": 0, "badges": [], "quiz_levels": {}}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {"tasks": [], "xp": 0, "badges": [], "quiz_levels": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==== GAMIFICATION ====
def calc_user_level(xp):
    return xp // 100 + 1

def next_level_xp(level):
    return level * 100

def xp_progress_percent(xp):
    level = calc_user_level(xp)
    return int((xp % 100) / 100 * 100)

def get_user_badges(xp):
    badges = []
    if xp >= 100: badges.append("Beginner 🐣")
    if xp >= 300: badges.append("Achiever 🏅")
    if xp >= 500: badges.append("Master 🌟")
    return badges

# ==== AI SUGGESTION ====
def get_ai_task():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = "Give me one fun and simple study task or wellness habit for a student."
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print("AI API error:", e)
        return "Read one page from your textbook 📘"

# ==== ADAPTIVE QUIZZES ====
quizzes_data = {
    1: {  # Python Basics
        "title": "Python Basics",
        "questions": {
            "easy": [
                {"question": "What is the keyword to define a function?", "options": ["A) func", "B) def", "C) function", "D) lambda"], "answer": "B", "xp": 5},
                {"question": "Which symbol is used for comments?", "options": ["A) //", "B) <!-- -->", "C) #", "D) /* */"], "answer": "C", "xp": 5},
            ],
            "medium": [
                {"question": "What does input() return by default?", "options": ["A) int", "B) str", "C) bool", "D) float"], "answer": "B", "xp": 10},
                {"question": "Which operator is used for exponentiation?", "options": ["A) ^", "B) **", "C) exp()", "D) ^^"], "answer": "B", "xp": 10},
            ],
            "hard": [
                {"question": "What is the output of: bool('False')?", "options": ["A) False", "B) True", "C) 0", "D) Error"], "answer": "B", "xp": 15},
                {"question": "Which of these is mutable?", "options": ["A) tuple", "B) string", "C) list", "D) frozenset"], "answer": "C", "xp": 15},
            ]
        }
    },
    2: {  # HTML & CSS
        "title": "HTML & CSS",
        "questions": {
            "easy": [
                {"question": "Which tag is used for the main heading?", "options": ["A) <h1>", "B) <p>", "C) <div>", "D) <head>"], "answer": "A", "xp": 5},
                {"question": "Which CSS property changes text color?", "options": ["A) font-color", "B) color", "C) text-color", "D) background"], "answer": "B", "xp": 5},
            ],
            "medium": [
                {"question": "Which tag creates a hyperlink?", "options": ["A) <link>", "B) <a>", "C) <href>", "D) <url>"], "answer": "B", "xp": 10},
                {"question": "Which property sets background color in CSS?", "options": ["A) bg-color", "B) color", "C) background-color", "D) background"], "answer": "C", "xp": 10},
            ],
            "hard": [
                {"question": "Which tag is used for table rows?", "options": ["A) <tr>", "B) <td>", "C) <table>", "D) <th>"], "answer": "A", "xp": 15},
                {"question": "Which CSS property controls spacing between letters?", "options": ["A) letter-spacing", "B) word-spacing", "C) line-height", "D) spacing"], "answer": "A", "xp": 15},
            ]
        }
    },
    3: {  # Logic & Thinking
        "title": "Logic & Thinking",
        "questions": {
            "easy": [
                {"question": "If all cats are mammals and all mammals are animals, are cats animals?", "options": ["A) Yes", "B) No", "C) Sometimes", "D) Cannot say"], "answer": "A", "xp": 5},
                {"question": "What comes next: 2, 4, 8, 16, ?", "options": ["A) 18", "B) 32", "C) 24", "D) 20"], "answer": "B", "xp": 5},
            ],
            "medium": [
                {"question": "Solve: 5x = 20, x = ?", "options": ["A) 2", "B) 3", "C) 4", "D) 5"], "answer": "C", "xp": 10},
                {"question": "If today is Monday, what day will it be in 45 days?", "options": ["A) Sunday", "B) Tuesday", "C) Wednesday", "D) Thursday"], "answer": "B", "xp": 10},
            ],
            "hard": [
                {"question": "Find the next prime after 47.", "options": ["A) 49", "B) 51", "C) 53", "D) 59"], "answer": "C", "xp": 15},
                {"question": "If all bloops are razzies and all razzies are luppies, are all bloops luppies?", "options": ["A) Yes", "B) No", "C) Cannot say", "D) Sometimes"], "answer": "A", "xp": 15},
            ]
        }
    },
    4: {  # AI Concepts
        "title": "AI Concepts",
        "questions": {
            "easy": [
                {"question": "What does AI stand for?", "options": ["A) Automated Internet", "B) Artificial Intelligence", "C) Automatic Input", "D) Advanced Innovation"], "answer": "B", "xp": 5},
                {"question": "Which is a machine learning task?", "options": ["A) Classification", "B) Painting", "C) Cooking", "D) Driving"], "answer": "A", "xp": 5},
            ],
            "medium": [
                {"question": "Neural networks are inspired by what?", "options": ["A) Animal nervous systems", "B) Quantum physics", "C) Architecture", "D) Music"], "answer": "A", "xp": 10},
                {"question": "Which is supervised learning?", "options": ["A) Clustering", "B) Regression", "C) Reinforcement", "D) None"], "answer": "B", "xp": 10},
            ],
            "hard": [
                {"question": "Which activation function outputs values between 0 and 1?", "options": ["A) ReLU", "B) Sigmoid", "C) Tanh", "D) Linear"], "answer": "B", "xp": 15},
                {"question": "Which learning algorithm uses rewards?", "options": ["A) Supervised", "B) Unsupervised", "C) Reinforcement", "D) Regression"], "answer": "C", "xp": 15},
            ]
        }
    }
}

# ==== ROUTES ====
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    data = load_data()
    xp = data.get("xp", 0)
    tasks = data.get("tasks", [])

    quizzes = [
        {"id": qid, "title": q["title"], "description": f"{len(q['questions']['easy'])}+ questions"} 
        for qid, q in quizzes_data.items()
    ]

    return render_template(
        "dashboard.html",
        tasks=tasks,
        user_level=calc_user_level(xp),
        user_xp=xp,
        next_level_xp=next_level_xp(calc_user_level(xp)),
        xp_percent=xp_progress_percent(xp),
        badges=get_user_badges(xp),
        suggested_task=get_ai_task(),
        checkin_tip=session.get("checkin_tip"),
        quizzes=quizzes
    )

@app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
def start_quiz(quiz_id):
    data = load_data()
    if "quiz_levels" not in data:
        data["quiz_levels"] = {}

    quiz = quizzes_data.get(quiz_id)
    if not quiz:
        return "Quiz not found!"

    # Determine current difficulty
    level = data["quiz_levels"].get(str(quiz_id), "easy")
    questions = quiz["questions"][level][:]
    random.shuffle(questions)

    if request.method == "POST":
        score = 0
        total_xp = 0
        for idx, q in enumerate(questions):
            user_answer = request.form.get(f"q{idx}")
            if user_answer and user_answer == q["answer"]:
                score += 1
                total_xp += q["xp"]

        data["xp"] += total_xp

        # Upgrade difficulty if score >= 80%
        percent = score / len(questions)
        next_level_msg = ""
        if percent >= 0.8:
            if level == "easy":
                data["quiz_levels"][str(quiz_id)] = "medium"
                next_level_msg = "Great! Next time you’ll get medium questions."
            elif level == "medium":
                data["quiz_levels"][str(quiz_id)] = "hard"
                next_level_msg = "Awesome! Next time you’ll get hard questions."

        save_data(data)
        return render_template(
            "quiz_result.html",
            quiz=quiz,
            questions=questions,
            score=score,
            total=len(questions),
            xp_earned=total_xp,
            next_level_msg=next_level_msg,
            request_form=request.form
        )

    return render_template("quiz.html", quiz=quiz, questions=questions, level=level)

@app.route("/add-task", methods=["POST"])
def add_task():
    data = load_data()
    task_name = request.form.get("task_name")
    new_task = {"id": len(data["tasks"]) + 1, "name": task_name, "completed": False, "xp": 20}
    data["tasks"].append(new_task)
    save_data(data)
    return redirect(url_for("dashboard"))

@app.route("/complete-task/<int:task_id>")
def complete_task(task_id):
    data = load_data()
    for t in data["tasks"]:
        if t["id"] == task_id and not t["completed"]:
            t["completed"] = True
            data["xp"] += t["xp"]
    save_data(data)
    return redirect(url_for("dashboard"))

@app.route("/checkin", methods=["POST"])
def checkin():
    mood = request.form.get("mood")
    tips = {
        "happy": "Keep that energy up! 🎉",
        "stressed": "Take a 5-min break and stretch 💆",
        "tired": "Power nap or hydrate 💧",
        "anxious": "Try deep breathing 🧘",
        "okay": "Steady progress is still progress 💪"
    }
    session["checkin_tip"] = tips.get(mood, "")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    print("Loaded Gemini API key:", bool(GEMINI_API_KEY))
    app.run(debug=True)
