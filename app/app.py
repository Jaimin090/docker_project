from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)

# PostgreSQL Configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'studentdb')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.String(50), unique=True, nullable=False)
    studentName = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    presentDate = db.Column(db.String(50), nullable=False)

# Fix: Create tables only once when the app starts
@app.before_first_request
def create_tables():
    db.create_all()

# Home Route
@app.route('/')
def home():
    return render_template('student.html')

# POST Route to Add Student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    try:
        new_student = Student(
            studentID=data['studentID'],
            studentName=data['studentName'],
            course=data['course'],
            presentDate=data['presentDate']
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"message": "Student added successfully"}), 201
    except IntegrityError:
        db.session.rollback()  # Roll back the transaction if duplicate
        return jsonify({"error": "Student already exists"}), 409
    except Exception as e:
        db.session.rollback()  # Roll back for other errors
        return jsonify({"error": str(e)}), 400

# GET Route to Fetch Students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{
        "studentID": student.studentID,
        "studentName": student.studentName,
        "course": student.course,
        "presentDate": student.presentDate
    } for student in students])

# PUT Route to Update Student Record
@app.route('/student/<studentID>', methods=['PUT'])
def update_student(studentID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON format"}), 400
    student = Student.query.filter_by(studentID=studentID).first()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    try:
        updated = False 
        # Update fields if provided in the request
        if "studentName" in data:
            student.studentName = data["studentName"]
        if "course" in data:
            student.course = data["course"]
        if "presentDate" in data:
            student.presentDate = data["presentDate"]

        db.session.commit()
        return jsonify({"message": "Student updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
