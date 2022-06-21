from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #ar gvinda modifikaciebis trrackingi
app.config["JWT_SECRET_KEY"] = "our-secret-key" #must be changed

db = SQLAlchemy(app)
jwt = JWTManager(app)

resource_users = {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "password": fields.String
}

resource_students = {            #stringad rom gadaiqces rata postmenma waikitxos user getshi
    "student_id": fields.Integer,
    "student_name": fields.String,
    "birth_date": fields.String,
    "student_faculty": fields.String
}
resource_exams = {
    "exam_id": fields.Integer,
    "exam_score": fields.Integer,
    "subject_name": fields.String,
    "std_id": fields.Integer
}

resource_register = {
    "username": fields.String,
    "email": fields.String,
    "password": fields.String
}


registerparser = reqparse.RequestParser()
registerparser.add_argument("username", type=str, help='user_name must be string')
registerparser.add_argument("email", type=str, required=True, help='Email must be string')
registerparser.add_argument("password", type=str, required=True, help='Email must be string')

userparser = reqparse.RequestParser()
userparser.add_argument("username", type=str, help='user_name must be string')
userparser.add_argument("email", type=str, help='Email must be string')
userparser.add_argument("password", type=str, help='Email must be string')

studentparser = reqparse.RequestParser()
studentparser.add_argument("student_id", type=int, help='Id must be integer')
studentparser.add_argument("student_name", type=str, help='Student_name must be string')
studentparser.add_argument("birth_date", type=str, help='Birth date must be string')
studentparser.add_argument("student_faculty", type=str, help='Death date must be string')

examparser = reqparse.RequestParser()
examparser.add_argument("exam_id", type=int, help='Id must be integer')
examparser.add_argument("exam_score", type=int, help='Title must be integer')
examparser.add_argument("subject_name", type=str, help='Body must be string')
examparser.add_argument("std_id", type=int, help='User_id must be integer')

class User(Resource):
    @marshal_with(resource_users)
    @jwt_required()
    def get(self, user_id):
        if user_id == 999:
            return UserModel.query.all()
        args = userparser.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        return user


    # @jwt_required()
    def post(self, user_id):
        args = userparser.parse_args()
        password = generate_password_hash(args["password"])
        user = UserModel(username=args["username"],email=args["email"], password=password)
        db.session.add(user)
        db.session.commit()
        return "inserted"


    # @jwt_required()
    def put(self, user_id):
        args = userparser.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        password = generate_password_hash(args["password"])
        if user == None:
            user = UserModel(username=args["username"], email=args["email"], password=password)
        else:
            user.username = args["username"]
            user.email = args["email"]
            user.password = password
        db.session.add(user)
        db.session.commit()
        return "updated"

    # @marshal_with(resource_user)
    # @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return f"User with id {user_id} has been deleted"

class Student(Resource):
    @marshal_with(resource_students)
    def get(self, student_id):
        if student_id == 999:
            return StudentsModel.query.all()
        # args = student_parser.parse_args()
        student = StudentsModel.query.filter_by(student_id=student_id).first()
        return student


    @jwt_required()
    def post(self, student_id):
        args = studentparser.parse_args()
        student = StudentsModel(student_name=args["student_name"], birth_date=args["birth_date"], student_faculty=args["student_faculty"])
        db.session.add(student)
        db.session.commit()
        return "inserted"


    @jwt_required()
    def put(self, student_id):
        args = studentparser.parse_args()
        student = StudentsModel.query.filter_by(student_id=student_id).first()
        if student == None:
            student = StudentsModel(student_name=args["student_name"], birth_date=args["birth_date"], student_faculty=args["death_date"])
        else:
            student.student_name = args["student_name"]
            student.birth_date = args["birth_date"]
            student.death_date = args["student_faculty"]
        db.session.add(student)
        db.session.commit()
        return "updated"


    @jwt_required()
    def delete(self, student_id):
        student = StudentsModel.query.filter_by(student_id=student_id).first()
        db.session.delete(student)
        db.session.commit()
        return f"Student with id {student_id} has been deleted"


class Exam(Resource):
    @marshal_with(resource_exams)
    def get(self, exam_id):
        if exam_id == 999:
            return ExamsModel.query.all()
        args = examparser.parse_args()
        exam = ExamsModel.query.filter_by(exam_id=exam_id).first()
        return exam


    @jwt_required()
    def post(self, exam_id):
        args = examparser.parse_args()
        if StudentsModel.query.filter_by(student_id=args["std_id"]).first():
            exam = ExamsModel(exam_score=args["exam_score"], subject_name=args["subject_name"], std_id=args["std_id"])
            db.session.add(exam)
            db.session.commit()
            return "Item has been inserted!"
        else:
            return "Given student_id doesn't exist"


    @jwt_required()
    def put(self, exam_id):
        args = examparser.parse_args()
        exam = ExamsModel.query.filter_by(exam_id=exam_id).first()
        if exam == None:
            exam = ExamsModel(exam_score=args["exam_score"], subject_name=args["subject_name"], std_id=args["std_id"])
        else:
            exam.exam_score = args["exam_score"]
            exam.subject_name = args["subject_name"]
            exam.std_id = args["std_id"]
        db.session.add(exam)
        db.session.commit()
        return "updated"

    # @marshal_with(resource_exams)
    @jwt_required()
    def delete(self, exam_id):
        exam = ExamsModel.query.filter_by(exam_id=exam_id).first()
        db.session.delete(exam)
        db.session.commit()
        return f"Exam with id {exam_id} has been deleted"



class Register(Resource):
    @marshal_with(resource_register)
    def post(self):
        args = registerparser.parse_args()
        user = UserModel(username=args["username"], email=args["email"], password=generate_password_hash(args["password"]))
        db.session.add(user)
        db.session.commit()
        return {"msg": "Created"}, 201

class Auth(Resource):
    # @marshal_with(resource_users)
    def post(self):
        email = request.json.get("email", None)
        password = request.json.get("password", None)

        user = UserModel.query.filter_by(email=email).first_or_404()
        if user is not None and check_password_hash(user.password, password) is True:
            access_token = create_access_token(identity=user.username)
            return jsonify(access_token=access_token)
        else:
            return jsonify({"msg": "Email or password is wrong"})


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"User {self.username}"

class StudentsModel(db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.String(20), nullable=False)
    student_faculty = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Syudent {self.student_name}"

class ExamsModel(db.Model):
    __tablename__ = 'exams'
    exam_id = db.Column(db.Integer, primary_key=True)
    exam_score = db.Column(db.Integer, nullable=False)
    subject_name = db.Column(db.String(80), nullable=False)
    std_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False) #შეამოწმე

    def __repr__(self):
        return f"Exam {self.subject_name}"

#მონაცემთა ბაზის შექმნა

user_data = [{"id": "1", "username": "Nika Tsitskishvili", "email": "n.tsitskishvili@gmail.com", "password": "astalavista"}, {"user_id": "2", "username": "Emilly Berger", "email": "e.berger@gmail.com", "password": "wonderpas"},
             {"id": "3", "username": "James Hope", "email": "j.hope@yahoo.com", "password": "amptylife123"},{"user_id": "4", "username": "Ketty Higgins", "email": "k.higgins.1@iliauni.@edu.ge", "password": "studentgreen"},
             {"id": "5", "username": "Harry Bing", "email": "h.bing@gmail.com", "password": "kenjimiazava2021"}]

student_data = [{"student_id": 1, "student_name": "ერთაოზ ბრეგაძე", "birth_date": "18/05/1997", "student_faculty": "ზუსტ და საბუნებისმეტყველო მეცნიერებათა ფაკულტეტი"},
                {"student_id": 1, "student_name": "ერთაოზ ბრეგაძე","birth_date": "18/05/1997","student_faculty": "ზუსტ და საბუნებისმეტყველო მეცნიერებათა ფაკულტეტი"},
                {"student_id": 2, "student_name": "მანუჩარ ხომასურიძე","birth_date": "16/03/1996","student_faculty": "ბიზნესის ადმინისტრირების ფაკულტეტი"},
                {"student_id": 3, "student_name": "ნატა კეკელია","birth_date": "3/01/1999","student_faculty": "სამედიცინო ფაკულტეტი"},
                {"student_id": 4, "student_name": "ნინო ქარდავა","birth_date": "24/08/1997","student_faculty": "საგარეო საქმეთა ურთიერთობების ფაკულტეტი"},
                {"student_id": 5, "student_name": "გიორგი გეგეჭური","birth_date": "13/11/2000","student_faculty": "ზუსტ და საბუნებისმეტყველო მეცნიერებათა ფაკულტეტი"}
                ]

exam_data = [{"exam_id": 1, "exam_score": 70, "subject_name": "ციფრული მარკეტინგი", "std_id": 2},
             {"exam_id": 2, "exam_score": 70,"subject_name":"ელექტრონიკის შესავალი", "std_id": 1},
             {"exam_id": 3, "exam_score": 70,"subject_name":"პოლიტოლოგიის შესავალი", "std_id": 4},
             {"exam_id": 4, "exam_score": 70,"subject_name":"მიკრობიოლოგიის შესავალი", "std_id": 5},
             {"exam_id": 5, "exam_score": 70,"subject_name":"ანატომიის შესავალი", "std_id": 3}

             ]
def create_database():
    for i in user_data:
        user = UserModel(username=i["username"], email=i["email"], password=generate_password_hash(i["password"]))
        db.session.add(user)
        db.session.commit()
    for i in student_data:
        student = StudentsModel(student_name=i["student_name"], birth_date=i["birth_date"], student_faculty=i["student_faculty"])
        db.session.add(student)
        db.session.commit()
    for i in exam_data:
        exam = ExamsModel(exam_score=i["exam_score"], subject_name=i["subject_name"], std_id=i["std_id"])
        db.session.add(exam)
        db.session.commit()

# @app.before_first_request
# def before_first_request():
#     db.create_all()
#     create_database()



api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Student, '/student/<int:student_id>')
api.add_resource(Exam, '/exam/<int:exam_id>')
api.add_resource(Auth, '/login')
api.add_resource(Register, '/register')



if __name__ == "__main__":
    app.run(debug=True)

