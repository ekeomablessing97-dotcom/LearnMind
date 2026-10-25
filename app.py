from flask import Flask, render_template, request, jsonify, session
import logging

app = Flask(__name__)
app.secret_key = "learnmind_super_secure_production_key"

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory user database storage
USERS_DB = {}

# Lesson Data Catalog
LESSONS = [
    {
        "id": "chem-intro-matter",
        "subject": "Chemistry",
        "title": "Matter and Separating Techniques",
        "level": "Senior Secondary",
        "topic": "Introduction to Chemistry",
        "summary": "Learn states of matter, physical vs. chemical changes, and methods of separating mixtures.",
        "explanation": "Matter is anything that has mass and occupies space. It exists in three primary states: solid, liquid, and gas. Mixtures consist of two or more substances combined physically and can be separated using techniques like evaporation, distillation, filtration, and chromatography.",
        "example": "Using simple distillation to purify salty water.",
        "steps": [
            "Identify if the substance is a pure element/compound or a physical mixture.",
            "Select the physical property difference (e.g., boiling point, particle size).",
            "Apply the appropriate separation technique."
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
                "feedback": "Melting ice changes state without altering its chemical composition."
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

# Health-check route to keep Render awake
@app.route('/ping')
def ping():
    return jsonify({"status": "active"}), 200

# API Signup Route
@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json(silent=True) or {}
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')

        if not name or not email or not password:
            return jsonify({"success": False, "error": "Please fill in all required fields."}), 400

        if email in USERS_DB:
            return jsonify({"success": False, "error": "This email is already registered. Please log in."}), 400

        USERS_DB[email] = {
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "is_pro": False
        }
        
        session['user'] = {"name": name, "email": email, "is_pro": False}
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500

# API Login Route
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
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500

# API Logout Route
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

# API Pro Upgrade Route
@app.route('/api/upgrade-pro', methods=['POST'])
def api_upgrade_pro():
    if 'user' in session:
        email = session['user']['email']
        if email in USERS_DB:
            USERS_DB[email]['is_pro'] = True
        session['user']['is_pro'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Not logged in"}), 401

if __name__ == '__main__':
    app.run(debug=False, port=5000)
