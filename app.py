from flask import Flask, render_template, request, jsonify, session
import logging

app = Flask(__name__)
app.secret_key = "learnmind_secure_key_for_production_stability"

# Configure logging to track any issues safely in Render logs
logging.basicConfig(level=logging.INFO)

# In-memory user store (Ready for database integration if needed)
USERS_DB = {}

# Comprehensive Lesson Data Structure
LESSONS = [
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
        "media_type": "image",
        "media_url": "https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?auto=format&fit=crop&w=800&q=80",
        "questions": [
            {
                "q": "Which state of matter has a definite volume but no definite shape?",
                "options": ["Solid", "Liquid", "Gas", "Plasma"],
                "answer": 1,
                "feedback": "Liquids take the shape of their container while maintaining a fixed volume."
            },
            {
                "q": "Which of the following is a physical change?",
                "options": ["Burning wood", "Rusting iron", "Melting ice", "Cooking an egg"],
                "answer": 2,
                "feedback": "Melting ice changes its state without altering its chemical composition."
            },
            {
                "q": "Which separation method is best suited for separating a mixture of miscible liquids with different boiling points?",
                "options": ["Filtration", "Fractional distillation", "Evaporation to dryness", "Magnetic separation"],
                "answer": 1,
                "feedback": "Fractional distillation relies on differing boiling points to separate miscible liquids."
            }
        ]
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
        "media_type": "image",
        "media_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80",
        "questions": [
            {
                "q": "When balancing the equation: Fe + Cl₂ → FeCl₃, what is the stoichiometric coefficient for Cl₂?",
                "options": ["1", "2", "3", "1.5"],
                "answer": 2,
                "feedback": "Balanced equation is 2Fe + 3Cl₂ → 2FeCl₃, so the coefficient for Cl₂ is 3."
            },
            {
                "q": "What is the relative molecular mass of water (H₂O)? [H=1, O=16]",
                "options": ["16", "18", "20", "2"],
                "answer": 1,
                "feedback": "(2 × 1) + 16 = 18."
            }
        ]
    }
]

@app.route('/')
def home():
    user = session.get('user')
    return render_template('index.html', user=user, lessons=LESSONS)

@app.route('/lessons')
def lessons_list():
    user = session.get('user')
    return render_template('lessons.html', user=user, lessons=LESSONS)

@app.route('/lesson/<lesson_id>')
def view_lesson(lesson_id):
    user = session.get('user')
    lesson = next((l for l in LESSONS if l["id"] == lesson_id), LESSONS[0])
    user_pro = user and user.get('is_pro', False)
    return render_template('lesson.html', lesson=lesson, user=user, user_pro=user_pro)

# Health-check route for Render uptime monitoring
@app.route('/ping')
def ping():
    return jsonify({"status": "active", "app": "LearnMind"}), 200

# --- AUTH API ENDPOINTS ---
@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json(silent=True) or {}
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')

        if not name or not email or not password:
            return jsonify({"success": False, "error": "All required fields must be filled."}), 400

        if email in USERS_DB:
            return jsonify({"success": False, "error": "Email already registered. Please log in."}), 400

        USERS_DB[email] = {"name": name, "email": email, "password": password, "phone": phone, "is_pro": False}
        session['user'] = {"name": name, "email": email, "is_pro": False}
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": f"Server Exception: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json(silent=True) or {}
        email = data.get('email')
        password = data.get('password')

        user = USERS_DB.get(email)
        if not user or user['password'] != password:
            return jsonify({"success": False, "error": "Invalid email or password."}), 401

        session['user'] = {"name": user['name'], "email": user['email'], "is_pro": user['is_pro']}
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": f"Server Exception: {str(e)}"}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/upgrade-pro', methods=['POST'])
def api_upgrade_pro():
    if 'user' in session:
        email = session['user']['email']
        if email in USERS_DB:
            USERS_DB[email]['is_pro'] = True
        session['user']['is_pro'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Not logged in"}), 401

# Global Error Handler so users never see raw server crashes
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Server error. Please refresh and try again."}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
