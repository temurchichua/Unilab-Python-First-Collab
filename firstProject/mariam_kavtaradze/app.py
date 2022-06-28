from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask import jsonify
import sqlite3

app = Flask(__name__)
api = Api(app)

items = [
    (0, "item_0", 20),
    (1, "item_1", 21),
    (2, "item_2", 22),
]

connection = sqlite3.connect('my_data.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, name TEXT, price REAL)")
query_items = "INSERT INTO items VALUES(?, ?, ?)"
cursor.executemany(query_items, items)
connection.commit()


class ItemModel:
    def __init__(self, _id, name, price):
        self.id = _id
        self.name = name
        self.price = price

    def __repr__(self):
        return f'id: {self.id} - name: {self.name} - price: {self.price}'

    @classmethod
    def find_by_itemid(cls, item_id):
        query = 'SELECT * FROM items WHERE id=?'
        result = cursor.execute(query, (item_id,))
        row = result.fetchone()
        if row:
            item = cls(*row)
        else:
            item = None
        return item

    @classmethod
    def insert_item(cls, new_item):
        query_items = "INSERT INTO items VALUES(?, ?, ?)"
        cursor.executemany(query_items, (new_item,))
        connection.commit()
        return new_item

    @classmethod
    def update_item(cls, updated_item, item_id):
        query = 'UPDATE items SET id = ?, name = ?, price = ? WHERE id = ?'
        cursor.execute(query, (*updated_item.values(), item_id, ))
        connection.commit()
        return updated_item


class ItemResource(Resource):
    item_parser = reqparse.RequestParser()
    item_parser.add_argument('id',
                             type=int,
                             required=True,
                             help="'id' argument must be in your request"
                             )
    item_parser.add_argument('name',
                             type=str,
                             required=True,
                             help="'name' argument must be in your request"
                             )
    item_parser.add_argument('price',
                             type=str,
                             required=True,
                             help="'price' argument must be in your request"
                             )

    def get(self, item_id):
        item = ItemModel.find_by_itemid(item_id)
        return {"message": f'current item: {item}'}, 200 if item is not None else 404

    def post(self, item_id):
        item = ItemModel.find_by_itemid(item_id)
        if item:
            return {"message": f"data with id {item_id} already exists"}, 400
        params = ItemResource.item_parser.parse_args()
        new_item = (item_id, params["name"], params["price"])
        ItemModel.insert_item(new_item)
        return {"message": f"created new item with id {item_id}"}, 200

    def put(self, item_id):
        item = ItemModel.find_by_itemid(item_id)
        params = ItemResource.item_parser.parse_args()
        if item:
            item.update_item(params, item_id)
            return {"message": f"updated item with id {item_id}. Updated version: {item}"}, 200
        new_item = (item_id, params["name"], params["price"])
        ItemModel.insert_item(new_item)
        return {"message": f"data with id {item_id} not found, so we created a new one for you: {new_item}"}, 404

    def delete(self, item_id):
        item = ItemModel.find_by_itemid(item_id)
        if item:
            query = "DELETE FROM items WHERE id = ?"
            cursor.execute(query, (item_id, ))
            connection.commit()
            return {"message": f"deleting item {item}."}, 200
        return {"message": f"data with id {item_id} not found"}, 404


class ItemsListResource(Resource):
    def get(self):
        items_db = cursor.execute("SELECT * FROM items")
        items = items_db.fetchall()
        return jsonify(items)

    def delete(self):
        query = "DELETE FROM items"
        cursor.execute(query)
        connection.commit()
        return {"message": f"all data has been removed from the list."}, 200


@app.route('/')
def index_get():
    return "successful"


api.add_resource(ItemResource, "/items/<int:item_id>")
api.add_resource(ItemsListResource, "/items")


if __name__ == '__main__':
    app.run(debug=True, port=5000)