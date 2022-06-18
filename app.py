from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import re

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SimpleMessenger.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super_buper_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

resource_account = {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String,
    "phone": fields.String,
}

resource_message = {
    "id": fields.Integer,
    "addressee": fields.String,
    "title": fields.String,
    "body": fields.String,
    "sender": fields.String
}

accountParser = reqparse.RequestParser()
accountParser.add_argument("account_id", type=int)
accountParser.add_argument("name", type=str)
accountParser.add_argument("email", type=str)
accountParser.add_argument("password", type=str)
accountParser.add_argument("phone", type=str)

messageParser = reqparse.RequestParser()
messageParser.add_argument("message_id", type=int)
messageParser.add_argument("addressee", type=str)
messageParser.add_argument("body", type=str)
messageParser.add_argument("title", type=str)
messageParser.add_argument("sender", type=str)

messages_accounts = db.Table("messages_accounts",
    db.Column("message_id", db.Integer, db.ForeignKey("MessageBox.id")),
    db.Column("account_id", db.Integer, db.ForeignKey("Accounts.id")))


class AccountModel(db.Model):
    __tablename__ = 'Accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return '<Account id %r>' % self.id


class MessageboxModel(db.Model):
    __tablename__ = 'MessageBox'
    id = db.Column(db.Integer, primary_key=True)
    addressee = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    body = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(50), db.ForeignKey('Accounts.email'), nullable=False)
    accounts = db.relationship("AccountModel", secondary=messages_accounts, lazy='dynamic', backref=db.backref("messages", lazy='dynamic'))

    def __repr__(self):
        return '<Message id %r>' % self.id


class Register(Resource):
    def post(self):
        args = accountParser.parse_args()
        _name = args["name"]
        _email = args["email"]
        _password = args["password"]
        _phone = args["phone"]
        if _name is None or _name == "":
            return {"msg": "Name field must not be empty"}, 406
        elif _email is None or _email == "":
            return {"msg": "Enter valid email address"}, 406
        elif _phone is None or _phone == "":
            return {"msg": "Enter valid phone number"}, 406
        elif (AccountModel.query.filter_by(phone=_phone).first() is not None) \
                or (AccountModel.query.filter_by(email=_email).first() is not None):
            return {"msg": "Phone number or/and Email is already used by another account"}, 409
        if _password is None or not is_valid_password(_password):
            return {"msg": "Password must contain at lest 8 letters, a number and a capital letter"}, 406

        account = AccountModel(name=_name, email=_email, password=generate_password_hash(_password),  phone=_phone)

        db.session.add(account)
        db.session.commit()
        return {"msg": "Your account has been successfully created"}, 201


class Auth(Resource):
    def post(self):
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        account = AccountModel.query.filter_by(email=email).first()
        if account is None or not check_password_hash(account.password, password):
            return {"msg": "Incorrect Email or Password"}, 401
        access_token = create_access_token(identity=account.id)
        return jsonify(access_token=access_token)


class Accounts(Resource):
    @marshal_with(resource_account)
    @jwt_required()
    def get(self, account_id):
        args = accountParser.parse_args()
        account = AccountModel.query.filter_by(id=account_id).first()
        if account_id == 0:
            return AccountModel.query.all()
        elif args["account_id"] is not None:
            return AccountModel.query.filter_by(id=args["account_id"]).first()
        elif args["email"] is not None:
            return AccountModel.query.filter_by(email=args["email"]).first()
        elif args["phone"] is not None:
            return AccountModel.query.filter_by(phone=args["phone"]).first()
        else:
            return account

    @jwt_required()
    def put(self, account_id):
        args = accountParser.parse_args()
        account = AccountModel.query.filter_by(id=account_id).first()
        account.email = args["email"] if args["email"] is not None else account.email
        account.phone = args["phone"] if args["phone"] is not None else account.phone
        if is_valid_password(args["password"]):
            account.password = generate_password_hash(args["password"])
        db.session.commit()
        return {"msg": "Changes has been saved"}, 202

    @jwt_required()
    def delete(self, account_id):
        account = AccountModel.query.filter_by(id=account_id).first()
        db.session.delete(account)
        db.session.commit()
        return {"msg": "Account has been deleted"}, 200


class Messagebox(Resource):
    @jwt_required()
    def post(self, account_id):
        account = AccountModel.query.filter_by(id=account_id).first()
        args = messageParser.parse_args()
        _addressee = args["addressee"]
        if _addressee is None \
                or _addressee == "" \
                or AccountModel.query.filter_by(email=_addressee).first() is None:
            return {"msg": "Enter valid receiver address"}, 404
        message = MessageboxModel(addressee=_addressee, title=args["title"], body=args["body"], sender=account.email)
        receiver = AccountModel.query.filter_by(email=message.addressee).first()
        message.accounts.append(account)
        message.accounts.append(receiver)
        db.session.add(message)
        db.session.commit()
        return {"msg": "Message has been sent"}, 200

    @marshal_with(resource_message)
    @jwt_required()
    def get(self, account_id):
        account = AccountModel.query.filter_by(id=account_id).first()
        args = messageParser.parse_args()
        all_msg = account.messages.order_by(MessageboxModel.id.desc())
        if args["addressee"] is not None:
            return all_msg.filter_by(addressee=args["addressee"]).all()
        elif args["sender"] is not None:
            return all_msg.filter_by(sender=args["sender"]).all()
        else:
            return all_msg.all()

    @jwt_required()
    def delete(self, account_id):
        account = AccountModel.query.filter_by(id=account_id).first()
        message = MessageboxModel.query.filter_by(id=messageParser.parse_args()["message_id"]).first()
        if message not in account.messages.all():
            return {"msg": "Choose a message from your MessageBox to delete"}, 404
        account.messages.remove(message)
        db.session.commit()
        if len(message.accounts.all()) == 0:
            db.session.delete(message)
            db.session.commit()
        return {"msg": "Message has been deleted"}, 200


class Welcome(Resource):
    def get(self):
        return {"Welcome page": "Simple Messenger",
                "gitHub": "https://github.com/ValerianQ/Repos"}


def is_valid_password(password):
    if password is not None \
            and len(password) >= 8 \
            and re.search('[0-9]', password) is not None \
            and re.search('[A-Z]', password) is not None:
            return True


api.add_resource(Welcome, '/')
api.add_resource(Auth, '/login')
api.add_resource(Register, '/register')
api.add_resource(Accounts, '/account/<int:account_id>')
api.add_resource(Messagebox, '/account/messagebox/<int:account_id>')


@app.before_first_request
def before_first_request():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
