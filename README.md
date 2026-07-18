# BuildByte-Codenyx
# SkillAI

> AI-powered skill verification platform connecting candidates and employers through real-time, automated assessments.

Built for **BuildByte Hackathon 2026**

---

## Team - CODENYX 

**Team Members:**
- Aleena Khalid - CS25056
- Laiba Qasim - CS25069

---

## Overview

SkillAI is a Flask-based web platform that lets candidates prove their skills through short, AI-evaluated assessments instead of relying on resumes alone. Candidates build a profile, select up to three skills, and take a 15-question assessment (multiple-choice + short-answer) for each. Multiple-choice answers are scored instantly, while short-answer responses are evaluated in real time by an LLM (via the Groq API), which returns a score and a one-line justification for each answer. Employers get a dedicated dashboard to browse verified candidate profiles and view detailed, skill-scored breakdowns — making it easier to shortlist talent based on demonstrated ability rather than claimed experience alone.

### Problem It Solves

Traditional hiring relies heavily on resumes and self-reported skills, which are hard to verify and often inflated. SkillAI closes that gap by giving candidates a fast way to demonstrate real competency, and giving employers a fast way to verify it — both in minutes, not days.

---

## Features

### For Candidates
- **Secure authentication** — registration and login with hashed passwords (Werkzeug)
- **Profile builder** — bio, portfolio links (GitHub/LinkedIn), and a featured project
- **Skill selection** — choose up to 3 skills to be assessed on (Graphic Design, Software Engineering, Teaching)
- **Dynamic assessments** — 15 questions per skill (mix of easy/medium/hard, MCQ + text-based), with a progress bar and question-by-question navigation
- **Instant results** — MCQs are auto-scored; text answers are evaluated by AI in real time, with a final combined percentage and a per-question breakdown

### For Employers
- **Employer dashboard** — browse all verified candidates in one place
- **Candidate detail view** — see a candidate's bio, verified skills, portfolio links, and featured project at a glance

### AI Integration
- Short-answer assessment responses are sent to an LLM (Groq — Llama 3.3 70B) for evaluation
- The model returns a structured score (out of 10) and reasoning for each answer, which is merged with MCQ results to produce a final weighted score

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, Jinja2 templates, Bootstrap 5, vanilla JavaScript |
| Auth | Werkzeug security (password hashing) |
| AI Evaluation | Groq API (Llama 3.3 70B Versatile) |
| Config | python-dotenv (environment variable management) |

---

## Project Structure

```
BuildByte-Codenyx/
│
├── app.py                  # Main Flask application (routes, logic)
├── database.py              # Script to initialize the SQLite database
├── questions.py              # Question bank for all assessments
├── requirements.txt          # Python dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── challenge.html
│   ├── assessment.html
│   ├── result.html
│   ├── employer.html
│   └── candidate_view.html
│
└── static/
    └── css/
        └── style.css
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+ installed
- pip (comes with Python)
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/buildbyte-<teamname>.git
cd buildbyte-<teamname>
```

**2. Install dependencies**
```bash
pip install -r requirements.txt --break-system-packages
```

> If you're not using a restricted Python environment, `pip install -r requirements.txt` works too.

**3. Initialize the database**
```bash
python database.py
```
This creates a local `skillai.db` SQLite file with the required `users` and `profiles` tables.

**4. Get a free Groq API key**
- Go to [console.groq.com/keys](https://console.groq.com/keys)
- Sign in with Google or GitHub
- Click **Create API Key** and copy it (no credit card required)

**5. Set up environment variables**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your-groq-api-key-here
```

**6. Run the app**
```bash
python app.py
```

**7. Open in your browser**
```
http://127.0.0.1:5000
```

---

## Dependencies (`requirements.txt`)

```
Flask
groq
python-dotenv
```

| Package | Purpose |
|---|---|
| `Flask` | Web framework — routing, templating, sessions |
| `groq` | Official Groq SDK — used to call the LLM for AI-based answer evaluation |
| `python-dotenv` | Loads environment variables (like `GROQ_API_KEY`) from a local `.env` file |

Standard library modules used (no install needed): `sqlite3`, `os`, `json`.

---

## How the Assessment Scoring Works

1. Each skill has 15 questions — a mix of multiple-choice and short-answer, across easy/medium/hard difficulty.
2. On submission:
   - MCQ answers are compared against the correct answer directly.
   - Short-answer responses are batched into a single prompt and sent to the Groq API, which returns a JSON list of `{id, score, reason}` for each answer.
3. MCQ and AI-graded answers are weighted equally (10 points each) and combined into one final percentage.
4. The result page shows the overall score plus a full breakdown — correct/incorrect for MCQs, and AI score + reasoning for text answers.

---

## Notes for Judges / Reviewers

- The `.env` file (containing the API key) and `skillai.db` (local database) are intentionally excluded from this repository via `.gitignore`, in line with standard security practice for handling credentials.
- To run the project, please follow the setup steps above and use your own free Groq API key.
- A live walkthrough/demo will be shown in person; this repo reflects the full working codebase behind that demo.

---

## Future Improvements

- Employer-side filtering/search by skill or score
- Badge/certificate generation for verified candidates
- Support for additional skill categories beyond the current three
- Timed assessments with auto-submit

---

## License

Built for BuildByte Hackathon 2026 — for educational and demonstration purposes.

- For any query: Contact aleenakhalid2007@gmail.com | desailaiba95@gmail.com 
- NED UNIVERSITY OF ENGINEERING & TECHNOLOGY, KARACHI