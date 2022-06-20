from flask import Flask, request
import sqlite3

app = Flask(__name__)

connection = sqlite3.connect('Students.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS students(
                    s_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(128),
                    score INTEGER DEFAULT 5)""")

cursor.close()
connection.close()


@app.route('/')
def index():
    return "Home Page"

@app.route('/students', methods=['GET'])
def get_students():
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()

    cursor.execute("""SELECT * FROM students""")
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    output = []
    if len(students) == 0:
        return "There are currently no students in Database."
    else:
        for item in students:
            student_info = {"ID": item[0], "name": item[1], "score": item[2]}
            output.append(student_info)
        return {"Students": output}


@app.route('/students/<id>', methods=['GET'])
def get_student(id):
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()

    cursor.execute("""SELECT * from STUDENTS where s_id = ?""", (id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()
    try:
        return {"ID": student[0], "name": student[1], "score": student[2]}
    except:
        return "There is no student with this ID"


@app.route('/students', methods=['POST'])
def add_student():
    student_name = request.json['name']
    student_score = request.json['score']

    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO students(name, score)
                        VALUES
                        (?, ?)""", (student_name, student_score))
    connection.commit()
    cursor.close()
    connection.close()

    return "Student added"


@app.route('/students/<id>', methods=['DELETE'])
def delete_student(id):
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()

    cursor.execute("""SELECT s_id FROM students""")
    id_list = cursor.fetchall()
    good_list = []
    for item in id_list:
        good_list.append(item[0])
    if int(id) in good_list:
        cursor.execute("""DELETE FROM students WHERE s_id = ?""", (id,))
        connection.commit()
        return "Student Deleted"
    else:
        return "There is no student with this ID"


@app.route('/students', methods=['PUT'])
def update_student():
    student_name = request.json['name']
    student_score = request.json['score']

    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()

    cursor.execute("""SELECT name FROM students""")
    name_list = cursor.fetchall()
    good_list = []
    for item in name_list:
        good_list.append(item[0])

    if student_name in good_list:
        cursor.execute("""UPDATE students SET  score = ? WHERE name = ?""", (student_score, student_name))
        connection.commit()
        cursor.close()
        connection.close()
        return "Student Score updated"

    else:
        cursor.execute("""INSERT INTO students
                            VALUES
                            (NULL, ?, ?)""", (student_name, student_score))
        connection.commit()
        cursor.close()
        connection.close()
        return "New Student added"



if __name__ == '__main__':
    app.run(debug=True)

