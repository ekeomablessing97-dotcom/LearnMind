from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pathlib import Path
import json
from datetime import date
import hashlib

app = Flask(__name__)
app.secret_key = "learnmind_ai_secure_secret_key_change_me"

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)
PROGRESS = DATA / "progress.json"
USERS_FILE = DATA / "users.json"

SUBJECTS = [
("Mathematics","Mathematics & Data","All levels","Numbers, algebra, geometry and statistics."),
("Further Mathematics","Mathematics & Data","Secondary","Advanced mathematical reasoning."),
("Physics","Science & Technology","Secondary","Motion, forces, energy and electricity."),
("Chemistry","Science & Technology","Secondary","Atoms, molecules, reactions and materials."),
("Biology","Science & Technology","Secondary","Cells, living things and ecosystems."),
("Computer Studies","Science & Technology","All levels","Computers, algorithms and digital skills."),
("Government","Social Sciences","Secondary","Political systems, constitutions and public institutions."),
("Social Studies","Social Sciences","Primary / Secondary","People, communities and society."),
("Economics","Business & Finance","Secondary","Choices, markets, demand and supply."),
("Accounting","Business & Finance","Secondary","Financial records and business accounts."),
("Commerce","Business & Finance","Secondary","Trade and activities supporting distribution."),
("Business Studies","Business & Finance","Primary / Secondary","Entrepreneurship and business operations."),
("English Language","Languages & Communication","All levels","Grammar, comprehension and communication."),
("Literature in English","Arts & Humanities","Secondary","Poetry, prose, drama and literary analysis."),
("History","Arts & Humanities","All levels","Past events and historical evidence."),
("Geography","Arts & Humanities","All levels","Places, maps, environments and landscapes."),
("Fine Arts","Arts & Humanities","All levels","Drawing, design and visual expression."),
("Civic Education","Social Sciences","Primary / Secondary","Rights, responsibilities and citizenship."),
("Agricultural Science","Practical & Vocational","Primary / Secondary","Crops, animals, soil and farming."),
("Home Economics","Practical & Vocational","Primary / Secondary","Food, family resources and everyday skills."),
("Technical Drawing","Practical & Vocational","Secondary","Technical sketches and drawing conventions."),
("Music","Arts & Humanities","All levels","Rhythm, melody and musical ideas."),
("French","Languages & Communication","All levels","French vocabulary and communication.")
]

LESSONS = [
# --- CHEMISTRY SYLLABUS ---
{
    "id": "chem-intro-matter",
    "subject": "Chemistry",
    "title": "Matter and Separating Techniques",
    "level": "Senior Secondary",
    "topic": "Introduction to Chemistry",
    "summary": "Learn states of matter, physical vs. chemical changes, and methods of separating mixtures.",
    "explanation": "Matter is anything that has mass and occupies space. It exists in three primary states: solid, liquid, and gas. Mixtures consist of two or more substances combined physically and can be separated using techniques like evaporation, distillation, filtration, and chromatography based on differences in physical properties.",
    "example": "Using filtration to separate sand from a mixture of sand and water, or using simple distillation to purify salty water.",
    "steps": [
        "Identify whether the substance is a pure element/compound or a physical mixture.",
        "Select a physical property difference (e.g., boiling point, particle size, magnetism).",
        "Apply the appropriate separation technique (e.g., fractional distillation for miscible liquids)."
    ],
    "question": "Which separation method is best suited for separating a mixture of water and ethanol (miscible liquids with different boiling points)?",
    "options": ["Filtration", "Fractional distillation", "Evaporation to dryness", "Magnetic separation"],
    "answer": 1,
    "feedback": "Fractional distillation separates miscible liquids based on their different boiling points."
},
{
    "id": "chem-particulate-nature",
    "subject": "Chemistry",
    "title": "Particulate Nature of Matter & Stoichiometry",
    "level": "Senior Secondary",
    "topic": "Symbols, Formulae and Equations",
    "summary": "Master atoms, molecules, relative atomic mass, mole concept, and balanced chemical equations.",
    "explanation": "A chemical equation represents a chemical reaction using symbols and formulae. Balancing equations ensures the law of conservation of mass is upheld—the number of atoms of each element on the reactant side must equal the product side.",
    "example": "Burning hydrogen in oxygen to form water: 2H₂ + O₂ → 2H₂O.",
    "steps": [
        "Write correct chemical formulae for all reactants and products.",
        "Count the number of atoms of each element on both sides.",
        "Use coefficients in front of formulas to balance atoms (never change subscripts inside formulas)."
    ],
    "question": "When balancing the equation: Fe + Cl₂ → FeCl₃, what is the stoichiometric coefficient for Cl₂?",
    "options": ["1", "2", "3", "1.5"],
    "answer": 2,
    "feedback": "Balanced equation is 2Fe + 3Cl₂ → 2FeCl₃, so the coefficient for Cl₂ is 3."
},

# --- PHYSICS SYLLABUS ---
{
    "id": "phys-motion-forces",
    "subject": "Physics",
    "title": "Kinematics and Newton's Laws of Motion",
    "level": "Senior Secondary",
    "topic": "Motion, Forces and Energy",
    "summary": "Analyze speed, velocity, acceleration, and Newton's laws governing physical forces.",
    "explanation": "Kinematics describes motion without considering its causes, using equations of motion ($v = u + at$, $s = ut + \\frac{1}{2}at^2$). Dynamics explores forces. Newton's second law states that force equals mass times acceleration ($F = ma$).",
    "example": "Calculating how long a car takes to stop under braking deceleration.",
    "steps": [
        "Identify given variables (initial velocity $u$, final velocity $v$, acceleration $a$, time $t$, distance $s$).",
        "Select the correct kinematic equation matching your known and unknown variables.",
        "Substitute values with proper SI units."
    ],
    "question": "A car accelerates uniformly from rest at 2 m/s² for 5 seconds. What is its final velocity?",
    "options": ["5 m/s", "10 m/s", "20 m/s", "2.5 m/s"],
    "answer": 1,
    "feedback": "Using $v = u + at$: $v = 0 + (2 \times 5) = 10$ m/s."
},

# --- BIOLOGY SYLLABUS ---
{
    "id": "bio-cell-structure",
    "subject": "Biology",
    "title": "Cell Structure and Organization",
    "level": "Junior / Senior Secondary",
    "topic": "The Cell as a Living Unit",
    "summary": "Explore plant and animal cell organelles, differences, and cellular organization.",
    "explanation": "The cell is the basic structural and functional unit of life. Animal cells contain a cell membrane, nucleus, cytoplasm, and mitochondria. Plant cells additionally possess a rigid cell wall, chloroplasts for photosynthesis, and a large central vacuole.",
    "example": "Comparing a factory (cell) with its power generator (mitochondria) and control center (nucleus).",
    "steps": [
        "Identify the cell type (plant vs. animal).",
        "Examine organelle structures and their specialized functions.",
        "Understand organization levels: Cell → Tissue → Organ → System → Organism."
    ],
    "question": "Which organelle is responsible for cellular respiration and energy (ATP) production?",
    "options": ["Ribosome", "Chloroplast", "Mitochondria", "Golgi body"],
    "answer": 2,
    "feedback": "Mitochondria are known as the powerhouse of the cell because they generate chemical energy (ATP)."
},

# --- MATHEMATICS SYLLABUS ---
{
    "id": "math-indices-log",
    "subject": "Mathematics",
    "title": "Indices, Logarithms and Surds",
    "level": "Senior Secondary",
    "topic": "Algebraic Processes",
    "summary": "Simplify powers, roots, and logarithmic expressions using standard mathematical laws.",
    "explanation": "Indices govern powers (e.g., $a^m \\times a^n = a^{m+n}$). Logarithms are the inverse of exponents (e.g., $\\log_a(xy) = \\log_a x + \\log_a y$). Surds deal with irrational square roots.",
    "example": "Simplifying complex exponential equations in commercial finance or scientific scaling.",
    "steps": [
        "Apply laws of indices for multiplication, division, and power of powers.",
        "Convert exponential equations to logarithmic form when solving for unknown exponents.",
        "Rationalize denominators when dealing with surds."
    ],
    "question": "Evaluate $\\log_{10} 1000$.",
    "options": ["2", "3", "10", "100"],
    "answer": 1,
    "feedback": "Since $10^3 = 1000$, $\\log_{10} 1000 = 3$."
},

# --- ECONOMICS SYLLABUS ---
{
    "id": "econ-demand-supply",
    "subject": "Economics",
    "title": "Theory of Demand and Supply",
    "level": "Senior Secondary",
    "topic": "Market Equilibrium",
    "summary": "Analyze consumer behavior, supply curves, price determination, and market equilibrium.",
    "explanation": "Demand is the quantity of a commodity consumers are willing and able to buy at various prices. Supply is what producers offer. Market equilibrium occurs where demand equals supply, setting the market clearing price.",
    "example": "When food scarcity hits, demand outstrips supply, causing market prices to spike.",
    "steps": [
        "Plot demand curve (downward sloping) and supply curve (upward sloping).",
        "Identify the point of intersection as market equilibrium.",
        "Analyze shifts caused by external factors like income changes or production costs."
    ],
    "question": "What happens to equilibrium price if consumer income increases for a normal good?",
    "options": ["Price decreases", "Price increases", "Price remains unchanged", "Supply becomes zero"],
    "answer": 1,
    "feedback": "Higher income increases demand, shifting the demand curve right and driving up the equilibrium price."
},

# --- GOVERNMENT SYLLABUS ---
{
    "id": "gov-constitution-fed",
    "subject": "Government",
    "title": "Constitutions and Federalism",
    "level": "Senior Secondary",
    "topic": "Political Institutions",
    "summary": "Examine types of constitutions, features of federalism, and separation of powers.",
    "explanation": "A constitution is the fundamental body of laws outlining how a state is governed. Federalism divides governmental powers between a central national government and constituent state/regional governments.",
    "example": "The division of legislative powers between the federal legislature and state assemblies.",
    "steps": [
        "Identify the structure of government (unitary vs. federal).",
        "Examine constitutional provisions and the supremacy of the constitution.",
        "Analyze organs of government: Legislature, Executive, and Judiciary."
    ],
    "question": "Which organ of government is primarily responsible for interpreting the laws?",
    "options": ["The Legislature", "The Executive", "The Judiciary", "The Civil Service"],
    "answer": 2,
    "feedback": "The judiciary interprets laws and administers justice in accordance with the constitution."
},

# --- ENGLISH LANGUAGE SYLLABUS ---
{
    "id": "eng-comprehension-summary",
    "subject": "English Language",
    "title": "Comprehension and Summary Writing",
    "level": "All levels",
    "topic": "Verbal Communication",
    "summary": "Develop reading fluency, context inference, and concise summary skills.",
    "explanation": "Comprehension tests your ability to extract meaning, tone, and specific details from passages. Summary writing requires extracting main points while eliminating redundant examples and descriptive fluff.",
    "example": "Summarizing a 500-word article into 3 precise sentences capturing the author's core argument.",
    "steps": [
        "Read through the passage quickly to grasp the general theme.",
        "Re-read carefully, underlining topic sentences and core arguments.",
        "Draft summaries using your own words while maintaining strict word limits."
    ],
    "question": "When writing a summary, which of the following should be avoided?",
    "options": ["Main ideas", "Personal opinions and lengthy examples", "Concise phrasing", "Key facts from text"],
    "answer": 1,
    "feedback": "Summaries must be objective; personal opinions, elaborate illustrations, and redundant examples should be excluded."
}
]

CATEGORIES = ["All subjects","Science & Technology","Mathematics & Data","Arts & Humanities","Social Sciences","Business & Finance","Languages & Communication","Practical & Vocational"]

def get_users():
    try: return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return []

def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")

def get_progress():
    try: return json.loads(PROGRESS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {"completed_lessons":[],"quiz_scores":[],"recall_notes":[]}

def save_progress(p): 
    PROGRESS.write_text(json.dumps(p,indent=2),encoding="utf-8")

@app.get("/")
def home(): 
    user = session.get("user")
    return render_template("index.html", categories=CATEGORIES, subject_count=len(SUBJECTS), lesson_count=len(LESSONS), user=user)

@app.get("/lessons/<lesson_id>")
def seo_lesson_page(lesson_id):
    l = next((x for x in LESSONS if x["id"] == lesson_id), None)
    if not l:
        return "Lesson not found", 404
    user = session.get("user")
    return render_template("lesson.html", lesson=l, user=user)

@app.post("/api/signup")
def signup():
    b = request.get_json(silent=True) or {}
    name = str(b.get("name","")).strip()
    email = str(b.get("email","")).strip().lower()
    password = str(b.get("password","")).strip()

    if not name or not email or not password:
        return jsonify(error="Please fill in all fields."), 400

    users = get_users()
    if any(u["email"] == email for u in users):
        return jsonify(error="An account with this email already exists."), 400

    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    new_user = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "is_pro": False
    }
    users.append(new_user)
    save_users(users)

    session["user"] = {"name": name, "email": email, "is_pro": False}
    return jsonify(success=True, name=name)

@app.post("/api/login")
def login():
    b = request.get_json(silent=True) or {}
    email = str(b.get("email","")).strip().lower()
    password = str(b.get("password","")).strip()

    if not email or not password:
        return jsonify(error="Please provide email and password."), 400

    users = get_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    user = next((u for u in users if u["email"] == email and u["password"] == hashed_pw), None)
    if not user:
        return jsonify(error="Invalid email or password."), 401

    session["user"] = {"name": user["name"], "email": user["email"], "is_pro": user.get("is_pro", False)}
    return jsonify(success=True, name=user["name"])

@app.post("/api/logout")
def logout():
    session.pop("user", None)
    return jsonify(success=True)

@app.get("/api/health")
def health(): return jsonify(status="ok", app="LearnMind", version="1.3", subjects=len(SUBJECTS), lessons=len(LESSONS))

@app.get("/api/subjects")
def subjects():
    q=request.args.get("q","").strip().casefold(); cat=request.args.get("category","All subjects"); level=request.args.get("level","All levels")
    out=[]
    for name,category,subject_level,description in SUBJECTS:
        if q and q not in name.casefold() and q not in category.casefold() and q not in description.casefold(): continue
        if cat!="All subjects" and category!=cat: continue
        if level!="All levels" and level.casefold() not in subject_level.casefold() and subject_level!="All levels": continue
        out.append({"name":name,"category":category,"level":subject_level,"description":description})
    return jsonify(out)

@app.get("/api/lessons")
def lessons():
    q=request.args.get("q","").strip().casefold(); subject=request.args.get("subject","All subjects"); out=[]
    for l in LESSONS:
        if subject!="All subjects" and l["subject"]!=subject: continue
        if q and q not in " ".join([l["title"],l["subject"],l["topic"],l["summary"]]).casefold(): continue
        out.append({k:v for k,v in l.items() if k not in ("options","answer","feedback","steps","explanation","example","question")})
    return jsonify(out)

@app.get("/api/lessons/<lesson_id>")
def lesson_detail(lesson_id):
    l=next((x for x in LESSONS if x["id"]==lesson_id),None)
    return (jsonify(l),200) if l else (jsonify(error="Lesson not found"),404)

@app.post("/api/check-answer")
def check_answer():
    b=request.get_json(silent=True) or {}; l=next((x for x in LESSONS if x["id"]==b.get("lesson_id")),None)
    if not l: return jsonify(error="Lesson not found"),404
    try: selected=int(b.get("answer"))
    except (TypeError,ValueError): return jsonify(error="Choose an answer first."),400
    correct=selected==l["answer"]; p=get_progress(); p["quiz_scores"].append({"lesson_id":l["id"],"correct":correct,"date":str(date.today())})
    if l["id"] not in p["completed_lessons"]: p["completed_lessons"].append(l["id"])
    save_progress(p); return jsonify(correct=correct,feedback=l["feedback"])

@app.post("/api/study-plan")
def study_plan():
    b = request.get_json(silent=True) or {}
    subject = str(b.get("subject", "your subject")).strip() or "your subject"
    goal = str(b.get("goal", "understand a topic")).strip() or "understand a topic"
    try: 
        mins = max(10, min(180, int(b.get("minutes", 30))))
    except (ValueError, TypeError): 
        mins = 30
    
    return jsonify(plan=[
        {"time": f"{mins // 6} min", "task": f"Review core syllabus definitions and principles for {subject} without notes."},
        {"time": f"{int(mins * 0.5)} min", "task": f"Deep dive into problem-solving, examples, and exam breakdowns for: {goal}."},
        {"time": f"{mins - (mins // 6) - int(mins * 0.5)} min", "task": "Attempt practice quiz questions, evaluate mistakes, and record revision notes."}
    ], note=f"Optimized {mins}-minute study session generated for {subject}.")

@app.post("/api/tutor")
def tutor():
    b=request.get_json(silent=True) or {}; q=str(b.get("question","")).strip()
    if not q: return jsonify(error="Type a question first."),400
    return jsonify(reply="Let's take it step by step. Upgrade to LearnMind Pro for unlimited AI tutor breakdowns!", mode="freemium tutor")

@app.get("/api/progress")
def progress(): return jsonify(get_progress())

if __name__=="__main__": app.run(debug=False,host="127.0.0.1",port=5000)