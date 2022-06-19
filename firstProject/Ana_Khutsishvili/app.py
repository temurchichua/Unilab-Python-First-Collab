from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String)
    language = db.Column(db.String)
    title = db.Column(db.String)

class BookSchema(ma.Schema):
    class Meta:
        fields = ('id','author','language','title')

book = BookSchema()
books = BookSchema(many=True)


@app.route('/books', methods=['POST'])
def add_book():
    author = request.json['author']
    language = request.json['language']
    title = request.json['title']
    new_book = Book(author=author,language=language,title=title)
    db.session.add(new_book)
    db.session.commit()
    return jsonify(book.dump(new_book))


@app.route('/books', methods=['GET'])
def get_book():
    all_books = Book.query.all()
    return jsonify(books.dump(all_books))


@app.route('/books/<int:id>', methods=['GET'])
def get_book_by_id(id):
    book_id = Book.query.get(id)
    return jsonify(book.dump(book_id))


@app.route('/books/<int:id>',methods=['PUT'])
def put_book(id):
    book_data = Book.query.get(id)
    book_data.author = request.json['author']
    book_data.language = request.json['language']
    book_data.title = request.json['title']
    db.session.commit()
    return jsonify(book.dump(book_data))


@app.route('/books/<int:id>',methods=['DELETE'])
def delete_book(id):
    book_data = Book.query.get(id)
    db.session.delete(book_data)
    db.session.commit()
    return jsonify(book.dump(book_data))



if __name__ == '__main__':
    app.run(debug=True)
