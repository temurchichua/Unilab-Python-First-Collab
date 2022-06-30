from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Book %r>' % self.title


if not os.path.isfile('books.db'):
    #  მონაცემთა ბაზას ვქმნი და მასში რამდენიმე მონაცემი შემაქვს
    db.create_all()
    book1 = Book(title='კაცია-ადამიანი?!', author='ილია ჭავჭავაძე')
    book2 = Book(title='ვეფხისტყაოსანი', author='შოთა რუსთაველი')
    db.session.add(book1)
    db.session.add(book2)
    db.session.commit()
    print(Book.query.all())


@app.route('/')
def index():
    return "Welcome to my API"


@app.route('/api/books/', methods=["GET"])
def get_books():
    books = Book.query.all()
    output = []
    for data in books:
        book_data = {"title": data.title, "author": data.author}
        output.append(book_data)

    return {'books': output}


@app.route('/api/books/<int:id>', methods=["GET"])
def get_book(id):
    book = Book.query.get_or_404(id)
    return {"title": book.title, "author": book.author}


@app.route('/api/books/', methods=["POST"])
def add_book():
    try:
        book = Book(title=request.json["title"], author=request.json["author"])
        db.session.add(book)
        db.session.commit()
        return {'id': book.id}
    except:
        return {'Error': "გთხოვთ მონაცემები სწორად შეიყვანოთ"}


@app.route('/api/books/<int:id>', methods=["PUT"])
def update_book(id):
    book = Book.query.get(id)
    if book is None:
        try:
            book = Book(title=request.json["title"], author=request.json["author"])
            db.session.add(book)
            db.session.commit()
            return 'New Record Created'
        except:
            return {'Error': "გთხოვთ მონაცემები სწორად შეიყვანოთ"}
    else:
        try:
            book.title = request.json["title"]
            book.author = request.json["author"]
            db.session.commit()
            return 'Record Updated'
        except:
            return {'Error': "გთხოვთ მონაცემები სწორად შეიყვანოთ"}


@app.route('/api/books/<int:id>', methods=["DELETE"])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return ""


if __name__ == '__main__':
    app.run(debug=True)
