from flask import Flask, jsonify, request, redirect
import sqlite3

app = Flask(__name__)

database_name = "genius.sqlite"

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect(database_name)
    except Exception as error_message:
        print(error_message)
    return conn

@app.before_first_request
def create_tables():
    tables = [
        """CREATE TABLE IF NOT EXISTS artists (
            ID INTEGER PRIMARY KEY UNIQUE,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            age INTEGER NOT NULL,
            country TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS songs (
            ID INTEGER PRIMARY KEY UNIQUE,
            album TEXT NOT NULL,
            song_name TEXT NOT NULL,
            song_style TEXT NOT NULL,
            BPM INTEGER NOT NULL,
            upload_date TEXT NOT NULL,
            artist_id INTEGER UNIQUE NOT NULL,
            FOREIGN KEY (artist_id) REFERENCES artists (ID)
        )"""
    ]
    conn = db_connection()
    cur = conn.cursor()
    for table in tables:
        cur.execute(table)

@app.route("/")
def home():
    return redirect("https://github.com/gigaamiridze/Genius-API")

# Artist's CRUD
@app.route("/artists", methods=["GET"])
def get_all_artist():
    conn = db_connection()
    cur = conn.cursor()
    cursor = cur.execute("SELECT * FROM artists")
    artists = [
        dict(ID=row[0], name=row[1], surname=row[2], age=row[3], country=row[4])
        for row in cursor.fetchall()
    ]
    return jsonify(artists), 200

@app.route("/artist/<int:artist_id>", methods=["GET"])
def get_artist_by_id(artist_id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM artists WHERE ID = ?", (artist_id,))
    row = cur.fetchone()
    if row is not None:
        artist = [
            dict(ID=row[0], name=row[1], surname=row[2], age=row[3], country=row[4])
        ]
        return jsonify(artist), 200
    return {"msg": f"Artist with ID {artist_id} could not be found"}, 404

@app.route("/artist", methods=["POST"])
def create_artist():
    conn = db_connection()
    cur = conn.cursor()
    artist_data = "INSERT INTO artists (name, surname, age, country) VALUES (?, ?, ?, ?)"
    name = request.args.get("name")
    surname = request.args.get("surname")
    age = request.args.get("age")
    country = request.args.get("country")
    cur.execute(artist_data, (name, surname, age, country))
    conn.commit()
    return {"msg": f"Artist with ID {cur.lastrowid} created successfully"}, 201

@app.route("/artist/<int:artist_id>", methods=["PUT", "DELETE"])
def put_delete_artist(artist_id):
    conn = db_connection()
    cur = conn.cursor()

    if request.method == "PUT":
        cur.execute("SELECT * FROM artists WHERE ID = ?", (artist_id,))
        artist = cur.fetchone()
        if artist is not None:
            artist_data = "UPDATE artists SET name = ?, surname = ?, age = ?, country = ? WHERE ID = ?"
            name = request.args["name"]
            surname = request.args["surname"]
            age = request.args["age"]
            country = request.args["country"]
            cur.execute(artist_data, (name, surname, age, country, artist_id))
            conn.commit()
            return {"msg": f"Artist with ID {artist_id} updated successfully"}, 200
        else:
            create_artist()
            return {"msg": f"Artist did not exist with this ID {artist_id} and was created"}, 201

    if request.method == "DELETE":
        cur.execute("DELETE FROM artists WHERE ID = ?", (artist_id,))
        conn.commit()
        return {"msg": f"Artist with ID {artist_id} has been deleted"}, 200

# Song's CRUD
@app.route("/songs", methods=["GET"])
def get_all_song():
    conn = db_connection()
    cur = conn.cursor()
    cursor = cur.execute("SELECT * FROM songs")
    songs = [
        dict(ID=row[0], album=row[1], song_name=row[2], song_style=row[3], BPM=row[4],
             upload_date=row[5], artist_id=row[6])
        for row in cursor.fetchall()
    ]
    return jsonify(songs), 200

@app.route("/song/<int:song_id>", methods=["GET"])
def get_song_by_id(song_id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs WHERE ID = ?", (song_id,))
    row = cur.fetchone()
    if row is not None:
        song = [
            dict(ID=row[0], album=row[1], song_name=row[2], song_style=row[3], BPM=row[4],
                 upload_date=row[5], artist_id=row[6])
        ]
        return jsonify(song), 200
    return {"msg": f"Song with ID {song_id} could not be found"}, 404

@app.route("/song", methods=["POST"])
def create_song():
    conn = db_connection()
    cur = conn.cursor()
    song_data = """INSERT INTO songs (album, song_name, song_style, BPM, upload_date, artist_id)
                    VALUES (?, ?, ?, ?, ?, ?)"""
    album = request.args.get("album")
    song_name = request.args.get("song_name")
    song_style = request.args.get("song_style")
    BPM = request.args.get("BPM")
    upload_date = request.args.get("upload_date")
    artist_id = request.args.get("artist_id")
    cur.execute(song_data, (album, song_name, song_style, BPM, upload_date, artist_id))
    conn.commit()
    return {"msg": f"Song with ID {cur.lastrowid} added successfully"}, 201

@app.route("/song/<int:song_id>", methods=["PUT", "DELETE"])
def put_delete_song(song_id):
    conn = db_connection()
    cur = conn.cursor()

    if request.method == "PUT":
        cur.execute("SELECT * FROM songs WHERE ID = ?", (song_id,))
        song = cur.fetchone()
        if song is not None:
            song_data = """UPDATE songs SET album = ?, song_name = ?, song_style = ?,
                            BPM = ?, upload_date = ?, artist_id = ? WHERE ID = ?"""
            album = request.args["album"]
            song_name = request.args["song_name"]
            song_style = request.args["song_style"]
            BPM = request.args["BPM"]
            upload_date = request.args["upload_date"]
            artist_id = request.args["artist_id"]
            cur.execute(song_data, (album, song_name, song_style, BPM, upload_date, artist_id, song_id))
            conn.commit()
            return {"msg": f"Song with ID {song_id} updated successfully"}, 200
        else:
            create_song()
            return {"msg": f"Song did not exist with this ID {song_id} and was created"}, 201

    if request.method == "DELETE":
        cur.execute("DELETE FROM songs WHERE ID = ?", (song_id,))
        conn.commit()
        return {"msg": f"Song with ID {song_id} has been deleted"}, 200

if __name__ == "__main__":
    app.run(port=7777, debug=True)