import mysql.connector


class Database(object):
    myDatabase = None
    my_cursor = None

    def __init__(self):
        self.myDatabase = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="corona_bot"
        )
        self.my_cursor = self.myDatabase.cursor()

    def insert_menu(self, menu_id, menu_name, menu_parent):
        sql = "INSERT INTO menus (id, name, parent) VALUES (%s, %s, %s)"
        val = (menu_id, menu_name, menu_parent)
        self.my_cursor.execute(sql, val)
        self.myDatabase.commit()

    def check_menu(self, menu_id):
        sql = "SELECT * FROM menus WHERE id ='" + str(menu_id) + "'"
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchall()
        if len(my_result) > 0:
            return True
        else:
            return False

    def add_status(self, user_id, parent_id):
        sql = "INSERT INTO track_user (user_id, parent_id) VALUES (%s, %s)"
        val = (user_id, parent_id)
        self.my_cursor.execute(sql, val)
        self.myDatabase.commit()
        print("user registered")

    def check_user(self, user_id):
        sql = "SELECT * FROM track_user WHERE user_id ='" + str(user_id) + "'"
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchall()
        if len(my_result) > 0:
            return True
        else:
            return False

    def get_parent_id(self, user_id):
        sql = "SELECT parent_id FROM track_user WHERE user_id ='" + str(user_id) + "'"
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchall()
        return my_result[0][0]

    def update_parent_id(self, user_id, parent_id):
        print("From DB:", parent_id)
        sql = "Update track_user set parent_id = '" + str(parent_id) + "' where user_id = '" + str(user_id) + "'"
        self.my_cursor.execute(sql)
        self.myDatabase.commit()
