import sqlite3

authorized = [
    "650496725554954261",
    "346474451254247424"
]


#
# cursor.execute('''CREATE TABLE if not exists authorization (
# id INTEGER PRIMARY KEY);''')

class DataBase():

    def __init__(self):
        PATH = "db\\auth.db"
        self.conn = sqlite3.connect(PATH)
        self.cursor = self.conn.cursor()
        owner = 650496725554954261

        """
        Create the database and set up the table if it does not exist.
        Add my user ID to admins
        """
        self.cursor.execute('''CREATE TABLE if not exists Admins (
        id INTEGER PRIMARY KEY,
        UserID INTEGER);''')

        owner_check = self.cursor.execute(f"SELECT * from Admins WHERE UserID == {owner}")
        if owner_check.fetchone() ==  None:
            self.cursor.execute("INSERT INTO Admins (UserID) VALUES (?)", (owner,))
            self.conn.commit()

    # Insert Member into Database
    def member_insert(self, data):
        self.data = data
        try:
            if not self.auth_check(data):
                self.cursor.execute("INSERT INTO Admins (UserID) VALUES (?)", (data,))
                self.conn.commit()
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(e)

    # Remove Member from Database
    def member_delete(self, data):
        self.data = data
        try:
            if self.auth_check(data):
                self.cursor.execute("DELETE FROM Admins WHERE UserID == (?)", (data,))
                self.conn.commit()
                return True
                # sanity_check = self.cursor.execute("SELECT * FROM Admins WHERE UserID = (?)", (data,))
                # if sanity_check == None:
                #     return True
            else:
                return False
        except sqlite3.Error as e:
            print(e)

    # Check discord member for Admin privilege
    def auth_check(self, member):
        self.member = member
        try:
            auth = self.cursor.execute("SELECT * FROM Admins WHERE UserID = (?)", (member,))
            if auth.fetchone() == None:
                return False
            else:
                return True
        except sqlite3.Error as e:
            print(e)

    def admin_list(self):
        try:
            adminlist = self.cursor.execute("SELECT UserID from Admins")
            return adminlist.fetchall()
        except sqlite3.Error as e:
            print(e)


    # When garbage collection comes around close the database
    def __del__(self):
        self.cursor.close()
        self.conn.close()



if __name__ == "__main__":
    member_auth = DataBase()
    member_auth.member_insert("123123123")
    member_auth.member_insert("222222222")
    member_auth.member_insert("333333333")

    if member_auth.auth_check("222222"):
        print("Authorization successful")
    else:
        print("Denied")
    member_auth.close_database()
   # member_auth.auth_check("123123123")



