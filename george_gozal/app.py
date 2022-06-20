from crypt import methods
from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import abort
from os import path

DB_NAME = "library.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def create_database():
    books = [
        {'title':'In Search of Lost Time ','author':'Marcel Proust','year':1913,'genre':'Modernist'},
        {'title':'Pride and Prejudice','author':'Jane Austen','year': 1813,'genre':'Romance novel'},
        {'title':'1984','author':'George Orwell','year': 1949,'genre':'Dystopian'},
        {'title':'The Great Gatsby','author':'F. Scott Fitzgerald','year': 1925,'genre':'Tragedy'},
        {'title':'Crime and Punishment','author':'Fyodor Dostoevsky','year': 1866,'genre':'Philosophical novel'},
        {'title':'Wuthering Heights','author':'Emily Brontë','year': 1847,'genre':'Romance'},
        {'title':'Of Mice and Men','author':'John Steinbeck','year': 1937,'genre':'Novels'},
        {'title':'Brave New World','author':'Aldous Huxley','year':1932 ,'genre':'Science Fiction'},
    ]
    if not path.exists(DB_NAME):
        db.create_all()
        print('Created Database!')

        for book in books:
            library_book = LibraryBook(
                title=book['title'],
                author=book['author'],
                year=book['year'],
                genre=book['genre']
            )
            db.session.add(library_book)
            db.session.commit()


class LibraryBook(db.Model):
    # __tablename__ = "library"
    __tablename__ = "library_book"
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    title = db.Column(db.String(150),nullable=False)
    author = db.Column(db.String(150))#,default='unknown')
    year = db.Column(db.Integer,nullable=False)
    genre = db.Column(db.String(150))

    def __repr__(self):
        return f"""
        Title: {self.title}
        Author: {self.author}
        Year: {self.year}
        Genre: {self.genre}"""

create_database()

@app.route('/')
def home():
    return """
        <ul>Hello to Api
        <li>/api/books GET # get all books </li>
        <li>/api/book/id GET # get single book by id </li>
        
        <li>/api/book POST # add book to database </li>
        <li>/api/book/id PUT # add new book or update by id </li>
        <li>/api/book/id DELETE # delete book by id </li>
        </ul>
        """

# get single book by id
@app.route('/api/book/<int:book_id>',methods=['GET'])
def get(book_id):
    book = LibraryBook.query.filter_by(id=book_id).first()
    if not book:
        abort(404,message="Could not find a book with that ID")
    else:
        return jsonify(
            {
                "id":book.id,
                "title":book.title,
                "author":book.author,
                "year":book.year,
                "genre":book.genre
                }
        )

# get all books list
@app.route('/api/books',methods=['GET'])
def get_all_books():
    books = LibraryBook.query.all()
    book_list = []
    for book in books:
        b = {
                "id":book.id,
                "title":book.title,
                "author":book.author,
                "year":book.year,
                "genre":book.genre
                }
            
        book_list.append(b)
    return jsonify(book_list)

# add data to database
@app.route('/api/book',methods=['POST'])
def post():        
    request_data = request.get_json()
    book = LibraryBook(
        title = request_data['title'],
        author = request_data['author'],
        year = request_data['year'],
        genre = request_data['genre']
        )
    db.session.add(book)
    db.session.commit()

    book = LibraryBook.query.order_by(LibraryBook.id.desc()).limit(1).first()

    book = {
                "id":book.id,
                "title":book.title,
                "author":book.author,
                "year":book.year,
                "genre":book.genre
                }
    return jsonify(book), 201

@app.route('/api/book/<int:book_id>',methods=['PUT'])
def put(book_id):
    request_data = request.get_json()
    book = LibraryBook.query.filter_by(id=book_id).first()
    print(book)
    if not book:
        new_book = LibraryBook(
            title = request_data['title'],
            author = request_data['author'],
            year = request_data['year'],
            genre = request_data['genre']
        )
        db.session.add(new_book)
        db.session.commit()
        print(new_book)
        print("New Book has been added")
    
    else:
        if request_data['title']:
                book.title = request_data['title']
        if request_data['author']:
                book.author = request_data['author']
        if request_data['year']:
                book.year = request_data['year']
        if request_data['genre']:
                book.genre = request_data['genre']

        db.session.commit()
        print("Book has been updated")
    
    book = LibraryBook.query.order_by(LibraryBook.id.desc()).limit(1).first()
    print(book)
    book = {
            "id":book.id,
            "title":book.title,
            "author":book.author,
            "year":book.year,
            "genre":book.genre
            }
    return jsonify(book)

@app.route('/api/book/<int:book_id>',methods=['DELETE'])
def delete(book_id):
    book = LibraryBook.query.filter_by(id=book_id).first()
    db.session.delete(book)
    db.session.commit()
    return f"Book with id {book_id} has been deleted"


if __name__ == '__main__':
    app.run(debug=True,port=5000)