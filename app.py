import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_FILE = "courses.json"

# Default sample data adhering to the lab schema
INITIAL_COURSES = [
    {
        "id": 1,
        "name": "Python Basics",
        "description": "Learn Python fundamentals",
        "target_date": "2025-12-31",
        "status": "Not Started",
        "created_at": "2025-11-04 10:30:00"
    }
]


# Helper 1: Read courses from JSON file (creates file if missing)
def load_courses():
    if not os.path.exists(DATA_FILE):
        save_courses(INITIAL_COURSES)
        return INITIAL_COURSES
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


# Helper 2: Write courses back to JSON file
def save_courses(courses):
    with open(DATA_FILE, "w") as f:
        json.dump(courses, f, indent=4)


# Helper 3: Generate new unique course ID
def get_next_id(courses):
    if not courses:
        return 1
    return max(course["id"] for course in courses) + 1


# --- API ENDPOINTS ---


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Retrieve all courses from the JSON file."""
    courses = load_courses()
    return jsonify({"success": True, "count": len(courses), "data": courses}), 200


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """Retrieve a single course by ID."""
    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return jsonify({"success": False, "error": "Course not found"}), 404
    return jsonify({"success": True, "data": course}), 200


@app.route("/api/courses", methods=["POST"])
def create_course():
    """Add a new course to the catalog and persist to JSON."""
    data = request.get_json() or {}

    if not data.get("name") or not data.get("description"):
        return jsonify({"success": False, "error": "Missing 'name' or 'description'"}), 400

    courses = load_courses()
    new_course = {
        "id": get_next_id(courses),
        "name": data.get("name"),
        "description": data.get("description"),
        "target_date": data.get("target_date", "2026-12-31"),
        "status": data.get("status", "Not Started"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    courses.append(new_course)
    save_courses(courses)
    return jsonify({"success": True, "data": new_course}), 201


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """Update existing course details or status."""
    data = request.get_json() or {}
    courses = load_courses()

    for course in courses:
        if course["id"] == course_id:
            course["name"] = data.get("name", course["name"])
            course["description"] = data.get("description", course["description"])
            course["target_date"] = data.get("target_date", course["target_date"])
            course["status"] = data.get("status", course["status"])

            save_courses(courses)
            return jsonify({"success": True, "data": course}), 200

    return jsonify({"success": False, "error": "Course not found"}), 404


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course from the JSON store."""
    courses = load_courses()
    filtered = [c for c in courses if c["id"] != course_id]

    if len(filtered) == len(courses):
        return jsonify({"success": False, "error": "Course not found"}), 404

    save_courses(filtered)
    return jsonify({"success": True, "message": f"Course {course_id} deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)