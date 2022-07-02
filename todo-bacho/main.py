from re import template
from flask import Flask , redirect,render_template , url_for, request, jsonify
import todo_db

app = Flask(__name__, template_folder="templetes")

#store

@app.route('/task',methods = ['POST'])
def store_todo():
    todo_db.sql_lite_base.todo_make_database()

    request_data = request.get_json()
    task = todo_db.Task()
    task.save(request_data)

    return jsonify({
        "message": "created successfully"
    })

#update

@app.route("/task/<int:task_id>", methods=['PUT'])

def update(task_id):
    todo_db.sql_lite_base.todo_make_database()

    task = todo_db.Task()
    request_data = request.get_json()

    if task.exist(task_id) == False:
        return jsonify(error=404, text = "Task not found"),404
    
    task.update(task_id, request_data)

    return jsonify({
        "message": "updated successfully"
    })

#get list

@app.route('/task', methods = ['GET'])
def index():
    todo_db.sql_lite_base.todo_make_database()

    task = todo_db.Task()
    tasks = task.get_list()
   
    return jsonify({
        "tasks": tasks
    })

#show task 

@app.route('/task/<int:task_id>', methods = ['GET'])
def show(task_id):
    todo_db.sql_lite_base.todo_make_database()
    task = todo_db.Task()

    if task.exist(task_id) == False:
        return jsonify(error=404, text = "Task not found"),404

    show_tasks = task.show(task_id)

    return jsonify({
        "task": show_tasks
    })

#delete task

@app.route('/task/<int:task_id>', methods = ['DELETE'])
def delete(task_id):
    todo_db.sql_lite_base.todo_make_database()
    task = todo_db.Task()

    if task.exist(task_id) == False:
        return jsonify(error=404, text = "Task not found"),404


    task.delete(task_id)
    return jsonify({
        "message": "deleted"
    })

 


