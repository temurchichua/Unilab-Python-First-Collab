from operator import contains
from connection import get_connection

class sql_lite_base:
        def todo_make_database():
            cursor,connection = get_connection()

            cursor.execute("""CREATE TABLE IF NOT EXISTS todo_list(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            content VARCHAR NOT NULL,
                            task_sender_id INTEGER ,
                            task_recipient_id INTEGER ,
                            deadline VARCHAR NOT NULL,

                            FOREIGN KEY (task_sender_id)
                            REFERENCES members_info (id), 
                            FOREIGN KEY (task_recipient_id)
                            REFERENCES members_info (id)
                             )""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS members_info(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nick_name VARCHAR NOT NULL

                             )""")
            
            connection.commit()

     

class User: 
    def insert_sender(self,user_name):  
        cursor,connection = get_connection()

        sender_script = f"insert into members_info values (NULL, '{user_name}')"
        cursor.execute(sender_script)
        connection.commit()

    def get_user_id(self,user_name):
        cursor,_ = get_connection()

        check_script = f"select nick_name from members_info where nick_name = '{user_name}'"
        cursor.execute(check_script)
        result = cursor.fetchone()
        result_type = f"{type(result)}"

        if result_type != "<class 'NoneType'>":
            select_query = f"select id from members_info where nick_name = '{user_name}'"
                    
            cursor.execute(select_query)
            user = cursor.fetchone()

            return user['id']
        elif result_type == "<class 'NoneType'>":
            self.insert_sender(user_name)
            select_query = f"select id from members_info where nick_name = '{user_name}'"
                
            cursor.execute(select_query)
            user = cursor.fetchone()

            return user['id']

 

class Task:
    def exist(self,user_id):
        cursor,_ = get_connection()

        exist_query = f"select id from todo_list where id = {user_id}"
        cursor.execute(exist_query)
        exist_check = False

        result = cursor.fetchone()
        result_type = f"{type(result)}"
        if result_type != "<class 'NoneType'>":
            exist_check = True
      
        return exist_check


    def save(self,request_data):
        cursor,connection = get_connection()

        user = User()        
        sender_id = user.get_user_id(request_data["sender"])
        receiver_id = user.get_user_id(request_data["receiver"])

        content_script = f"insert into todo_list values (NULL, '{request_data['content']}', '{sender_id}', '{receiver_id}', '{request_data['deadline']}')"
        cursor.execute(content_script)
        connection.commit()

        return True

    def update(self, task_id, request_data):
        cursor,connection = get_connection()

        user = User()        
        sender_id1 = user.get_user_id(request_data["sender"])
        receiver_id1 = user.get_user_id(request_data["receiver"])

        update_script = f"UPDATE todo_list set content = '{request_data['content']}', task_sender_id = {sender_id1}, task_recipient_id = {receiver_id1}, deadline = '{request_data['deadline']}' where id = '{task_id}'"
        cursor.execute(update_script)
        connection.commit()
        return True



    def get_list(self):
        cursor,_ = get_connection()

        cursor.execute(""" select todo_list.id, todo_list.content , il.nick_name as sender, il2.nick_name as receiver, todo_list.deadline
                            from todo_list 
                            inner join members_info as il on il.id = todo_list.task_sender_id
                            inner join members_info as il2 on il2.id = todo_list.task_recipient_id""")
        result5 = cursor.fetchall()
        return result5

    def show(self, task_id):
        cursor,_ = get_connection()

        show_user_query = f"select todo_list.id, todo_list.content , il.nick_name as sender, il2.nick_name as receiver, todo_list.deadline from todo_list  inner join members_info as il on il.id = todo_list.task_sender_id inner join members_info as il2 on il2.id = todo_list.task_recipient_id where todo_list.id = {task_id}"
        cursor.execute(show_user_query)
        
        result6 = cursor.fetchone()
        return result6

    def delete(self, task_id):
        cursor,connection = get_connection()
        
        delete_query = f"delete from todo_list where id = {task_id}"
        cursor.execute(delete_query)
        connection.commit()

        return "delete"