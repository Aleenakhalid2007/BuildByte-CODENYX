
from dotenv import load_dotenv
load_dotenv()
import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq
from questions import QUESTION_BANK

app = Flask(__name__)
app.secret_key = "buildbyte_secret_key_123"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DB_NAME = "skillai.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================
# Landing Page
# ==========================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================
# Register
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, role)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="Email already registered")
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================
# Login
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "employer":
                return redirect(url_for("employer"))
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ==========================
# Logout
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ==========================
# Dashboard (protected)
# ==========================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session.get("name"), role=session.get("role"))


# ==========================
# Profile
# ==========================
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()

    if request.method == "POST":
        bio = request.form.get("bio")
        skills = request.form.getlist("skills")  # checkboxes, max 3
        github = request.form.get("github")
        linkedin = request.form.get("linkedin")
        project_name = request.form.get("project_name")
        project_description = request.form.get("project_description")

        skills_str = ",".join(skills)

        existing = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        if existing:
            conn.execute("""
                UPDATE profiles
                SET bio=?, skills=?, github=?, linkedin=?, project_name=?, project_description=?
                WHERE user_id=?
            """, (bio, skills_str, github, linkedin, project_name, project_description, user_id))
        else:
            conn.execute("""
                INSERT INTO profiles (user_id, bio, skills, github, linkedin, project_name, project_description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, bio, skills_str, github, linkedin, project_name, project_description))

        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    profile_data = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return render_template("profile.html", profile=profile_data)


# ==========================
# Challenge (skill selection)
# ==========================
@app.route("/challenge")
def challenge():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    profile_data = conn.execute("SELECT skills FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    user_skills = []
    if profile_data and profile_data["skills"]:
        user_skills = profile_data["skills"].split(",")

    return render_template("challenge.html", user_skills=user_skills)


# ==========================
# Assessment (dynamic)
# ==========================
@app.route("/assessment")
def assessment():
    skill = request.args.get("skill", "software engineering")
    questions = QUESTION_BANK.get(skill, [])
    return render_template("assessment.html", questions=questions, skill=skill)


# ==========================
# Result (scoring + AI evaluation via Groq)
# ==========================
@app.route("/result", methods=["POST"])
def result():
    skill = request.form.get("skill", "software engineering")
    questions = QUESTION_BANK.get(skill, [])

    total = len(questions)
    correct = 0
    text_answers_for_ai = []
    breakdown = []

    for q in questions:
        qid = q["id"]
        user_answer = request.form.get(qid, "").strip()

        if q["type"] == "mcq":
            is_correct = user_answer.strip().lower() == q["answer"].strip().lower()
            if is_correct:
                correct += 1
            breakdown.append({
                "question": q["question"],
                "type": "mcq",
                "user_answer": user_answer,
                "correct_answer": q["answer"],
                "is_correct": is_correct
            })
        else:
            text_answers_for_ai.append({
                "id": qid,
                "question": q["question"],
                "user_answer": user_answer
            })

    ai_results = []
    if text_answers_for_ai:
        prompt = f"""You are evaluating a candidate's answers for a {skill} skill assessment.
For each question below, give a score out of 10 and a one-line reason.
Respond ONLY in valid JSON, as a list like:
[{{"id": "q3", "score": 7, "reason": "..."}}]

Questions and answers:
"""
        for item in text_answers_for_ai:
            prompt += f'\nID: {item["id"]}\nQuestion: {item["question"]}\nAnswer: {item["user_answer"]}\n'

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.choices[0].message.content.strip()
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            ai_results = json.loads(raw_text)
        except Exception as e:
            print("AI evaluation error:", e)
            ai_results = [{"id": item["id"], "score": 0, "reason": "AI evaluation failed"}
                           for item in text_answers_for_ai]

    ai_score_map = {r["id"]: r for r in ai_results}
    text_max_score = len(text_answers_for_ai) * 10
    text_score_earned = 0

    for item in text_answers_for_ai:
        ai_res = ai_score_map.get(item["id"], {"score": 0, "reason": "No AI response"})
        text_score_earned += ai_res.get("score", 0)
        breakdown.append({
            "question": item["question"],
            "type": "text",
            "user_answer": item["user_answer"],
            "ai_score": ai_res.get("score", 0),
            "ai_reason": ai_res.get("reason", "")
        })

    mcq_count = total - len(text_answers_for_ai)
    mcq_max = mcq_count * 10
    mcq_score_earned = correct * 10

    total_earned = mcq_score_earned + text_score_earned
    total_max = mcq_max + text_max_score
    percentage = round((total_earned / total_max) * 100) if total_max > 0 else 0

    return render_template(
        "result.html",
        skill=skill,
        percentage=percentage,
        correct=correct,
        total=total,
        breakdown=breakdown
    )


# ==========================
# Employer Dashboard
# ==========================
@app.route("/employer")
def employer():
    if "user_id" not in session or session.get("role") != "employer":
        return redirect(url_for("login"))

    conn = get_db_connection()
    candidates = conn.execute("""
        SELECT users.id, users.name, users.email, profiles.bio, profiles.skills,
               profiles.github, profiles.linkedin, profiles.project_name
        FROM users
        JOIN profiles ON users.id = profiles.user_id
        WHERE users.role = 'candidate'
    """).fetchall()
    conn.close()

    return render_template("employer.html", candidates=candidates)


# ==========================
# Candidate Detail View
# ==========================
@app.route("/candidate/<int:user_id>")
def candidate_view(user_id):
    if "user_id" not in session or session.get("role") != "employer":
        return redirect(url_for("login"))

    conn = get_db_connection()
    candidate = conn.execute("""
        SELECT users.id, users.name, users.email, profiles.bio, profiles.skills,
               profiles.github, profiles.linkedin, profiles.project_name, profiles.project_description
        FROM users
        JOIN profiles ON users.id = profiles.user_id
        WHERE users.id = ?
    """, (user_id,)).fetchone()
    conn.close()

    if not candidate:
        return "Candidate not found", 404

    return render_template("candidate_view.html", candidate=candidate)


# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app.run(debug=True)