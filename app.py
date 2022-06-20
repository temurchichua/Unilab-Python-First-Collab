import json
import string, sqlite3
from flask import Flask, jsonify, render_template, request, redirect, url_for
from random import choice, randint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect('students.db', check_same_thread=False)
c = conn.cursor()


c.execute("""CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY,full_name TEXT, subject TEXT, first_grade FLOAT
            , second_grade FLOAT, third_grade FLOAT, fourth_grade FLOAT, fifth_grade FLOAT)""")
conn.commit()
subjects = ["Python", "Java", "C++", "C", "JavaScript", "HTML", "CSS"]
names = ["John", "Mary", "Mike", "Jane", "Bob", "Sam", "Tom", "Alex", "Kate", "Linda", "Sara", "Sophia", "Emma"]



c.execute("SELECT * FROM students")
if len(c.fetchall()) == 0:   # პირველ გაშვებაზე ბაზა თუ ცარიელია სატესტოდ ვამატებ.
    c.execute('''insert into students(full_name, subject, first_grade, second_grade, third_grade, fourth_grade, fifth_grade) 
                values (?,?,?,?,?,?,?)''', (choice(names) , choice(subjects).lower(), 2, 0, 4, 0,3))
    c.execute('''insert into students(full_name, subject, first_grade, second_grade, third_grade, fourth_grade, fifth_grade) 
                values (?,?,?,?,?,?,?)''', (choice(names), choice(subjects).lower(), 2, 3, 4, 0,3))
    conn.commit()


# თითო გაშვებაზე რენდომულად ემატება სტუდენტი ბაზაში
c.execute('''insert into students(full_name, subject, first_grade, second_grade, third_grade, fourth_grade, fifth_grade)
            values (?,?,?,?,?,?,?)''', (choice(names), choice(subjects).lower(), randint(0,5), randint(0,5), randint(0,5), randint(0,5),randint(0,5)))
conn.commit()



global full_name, sub

@app.route('/result/<student_name>/<subject_name>', methods=['POST']) 
def result(student_name, subject_name):
    global name
    full_name = student_name
    sub = subject_name
    if request.method == 'POST': # აქ ვიღებთ /result/სტუდენტისსახელი/საგანი არგუმენტებიდან მონაცემებს(ქულებს) და ვაბრუნებთ სტუდენტის ინფორმაციას საგნებზე
        if ('.' not in str(request.args.get('ex1')) and not str(request.args.get('ex1')).isdigit()) or ('.' not in str(request.args.get('ex2')) and not str(request.args.get('ex2')).isdigit()) or ('.' not in str(request.args.get('ex3')) and not str(request.args.get('ex3')).isdigit()) or ('.' not in str(request.args.get('ex4')) and not str(request.args.get('ex4')).isdigit()) or ('.' not in str(request.args.get('ex5')) and not str(request.args.get('ex5')).isdigit()):
            error = "Please enter Correct numbers"
            return {'error': error}
        ex1 = float(request.args.get('ex1'))
        ex2 = float(request.args.get('ex2'))
        ex3 = float(request.args.get('ex3'))
        ex4 = float(request.args.get('ex4'))
        ex5 = float(request.args.get('ex5'))

        avg = (ex1 + ex2 + ex3 + ex4 + ex5) / 5
        sum = ex1 + ex2 + ex3 + ex4 + ex5
        min_score = 10.5
        if ex1 > 5 or ex1 < 1 or ex2 > 5 or ex2 < 1 or ex3 > 5 or ex3 < 1 or ex4 > 5 or ex4 < 1 or ex5 > 5 or ex5 < 1:
            error = "Please enter a number between 1 and 5"
            return {'error': error}
        if sum < min_score:
            c.execute('''update students set first_grade = ?, second_grade = ?, third_grade = ?, fourth_grade = ?, fifth_grade = ? where full_name = ? and subject = ?''', (ex1, ex2, ex3, ex4, ex5, full_name, sub))
            conn.commit()
            status = "No"
            return {'passed': status, 'avg': avg, 'sum': sum, 'min_score': min_score, 'name': full_name, 'subject': sub}
        elif sum >= min_score:
            c.execute('''update students set first_grade = ?, second_grade = ?, third_grade = ?, fourth_grade = ?, fifth_grade = ? where full_name = ? and subject = ?''', (ex1, ex2, ex3, ex4, ex5, full_name, sub))
            conn.commit()
            status = "Yes"
            return {'passed': status, 'avg': avg, 'sum': sum, 'min_score': min_score, 'name': full_name, 'subject': sub}

@app.route('/result', methods=['GET'])
def result_get():
    if request.method == 'GET': # ამ მეთოდით კი უბრალოდ ვაბრუნებთ სტუდენტის სტატისტიკას სსაგნებზე პირდაპირ ბაზიდან, avg, min score , გადალახა თუ არა და ა.შ
    
        student_infos = []
        c.execute('''select * from students''')
        for row in c.fetchall():
            avg = (row[3] + row[4] + row[5] + row[6] + row[7]) / 5
            sum = row[3] + row[4] + row[5] + row[6] + row[7]
            min_score = 10.5
            if sum < min_score:
                status = "No"
            elif sum >= min_score:
                status = "Yes"
            student_infos.append({"name": row[1], "subject": row[2],"avg" : avg, "sum" : sum,"min_score": min_score,"passed": status, "first_grade": row[3], "second_grade": row[4], "third_grade": row[5], "fourth_grade": row[6], "fifth_grade": row[7]})

        return jsonify(student_infos)

@app.route('/students/<id>') # აქ აიდის იღებს მისამართიდან და შესაბამისი student_id ის იუზერის დატა ბრუნდება
def students(id):
    students = []
    c.execute('''select * from students where student_id = ?''', (id,))
    for row in c.fetchall():
        students.append({"student_id": row[0],"name": row[1], "subject": row[2],"first_grade": row[3], "second_grade": row[4], "third_grade": row[5], "fourth_grade": row[6], "fifth_grade": row[7]})
    return jsonify(students)


@app.route('/students') # ამ ენდფოინთზე ბრუნდება ბაზიდან ყველა იუზერის დატა
def students_list():
    students = []
    c.execute('''select * from students''')
    for row in c.fetchall():
        students.append({"student_id": row[0],"name": row[1], "subject": row[2],"first_grade": row[3], "second_grade": row[4], "third_grade": row[5], "fourth_grade": row[6], "fifth_grade": row[7]})
    return jsonify(students)



@app.route('/add-student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        full_name = request.args.get('full_name')
        sub = request.args.get('subject')
        ex1 = float(request.args.get('ex1'))
        ex2 = float(request.args.get('ex2'))
        ex3 = float(request.args.get('ex3'))
        ex4 = float(request.args.get('ex4'))
        ex5 = float(request.args.get('ex5'))
        c.execute('''insert into students (full_name, subject, first_grade, second_grade, third_grade, fourth_grade, fifth_grade) values (?,?,?,?,?,?,?)''', (full_name, sub, ex1, ex2, ex3, ex4, ex5))
        conn.commit()
        return jsonify({"message": "Student added successfully"})


@app.route('/update-student', methods=['PUT'])
def update_student():
    if request.method == 'PUT':
        full_name_old = request.args.get('full_name_old')
        full_name_new = request.args.get('full_name')
        sub = request.args.get('subject')
        ex1 = float(request.args.get('ex1'))
        ex2 = float(request.args.get('ex2'))
        ex3 = float(request.args.get('ex3'))
        ex4 = float(request.args.get('ex4'))
        ex5 = float(request.args.get('ex5'))
        c.execute("""select * from students where full_name = ?""", (full_name_old,))
        data = c.fetchall()
        if len(data) == 0: # თუ ბაზაში ვერ იპოვე ამ სახელით არ დააპდეითებს
            return jsonify({"message": f"Student {full_name_old} not found"})
        c.execute('''update students set full_name = ?, subject = ?, first_grade = ?, second_grade = ?, third_grade = ?, fourth_grade = ?, fifth_grade = ? where full_name = ?''', (full_name_new,sub, ex1, ex2, ex3, ex4, ex5, full_name_old))
        conn.commit()
        return jsonify({"message": "Student updated successfully"})


@app.route('/delete-student', methods=['DELETE'])
def delete_student():
    if request.method == 'DELETE':
        full_name = request.args.get('full_name')
        c.execute("""select * from students where full_name = ?""", (full_name,))
        data = c.fetchall()
        if len(data) == 0: # თუ ბაზაში ვერ მოძებნა ამ სახელით არაფერს წაშლის და მესიჯს გამოატანს
            return jsonify({"message": f"Student {full_name} not found"})
        c.execute('''delete from students where full_name = ?''', (full_name,))
        conn.commit()
        return jsonify({"message": "Student deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)