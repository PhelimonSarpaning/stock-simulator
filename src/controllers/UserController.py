import mysql.connector, binascii, hashlib

from Models import User

class UserController:

    # TODO - turn into env variable
    CONN_STRING = "host='localhost' port=3306 user='root' password=''"

    @classmethod
    def findByUsername(cls, username: str) -> User:
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT * FROM UserTable WHERE username={username}")
            row = cursor.fetchone()
            if(row is None):
                return None

            user = User(row[0], row[1])
            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return None
        finally:
            if(connection is not None):
                connection.close()
            return user

    # Add balance to user account
    @classmethod
    def addBalance(cls, userId: int, amount: float):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT balance FROM UserTable WHERE id={userId}")
            row = cursor.fetchone()
            newBalance = row[0] + amount
            cursor.execute(f"UPDATE UserTable SET balance={newBalance} WHERE id={userId}")
            # TODO - this could be turned into a MySQL procedure
            cursor.execute(f"INSERT INTO UserBalanceHistory (user_id, balance) VALUES({userId}, {newBalance})")

            connection.commit()
            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return {"message": "Something went wrong"}
        finally:
            if(connection is not None):
                connection.close
            return {"message": "Add balance successful"}

    # Subtract balance from user account
    @classmethod
    def subtractBalance(cls, userId: int, amount: float):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()
            
            cursor.execute(f"SELECT balance FROM UserTable WHERE id={userId}")
            row = cursor.fetchone()
            newBalance = row[0] - amount
            # TODO - where/how do we want to handle overdrawing?
            cursor.execute(f"UPDATE UserTable SET balance={newBalance}")
            # TODO
            cursor.execute(f"INSERT INTO UserBalanceHistory (user_id, balance) VALUES({userId}, {newBalance})")

            connection.commit()
            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return {"message": "Something went wrong"}
        finally:
            if(connection is not None):
                connection.close()
            return {"message": "Subtract balance successful"}

    @classmethod
    def getUserBalanceHistory(cls, userId):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT balance FROM UserBalanceHistory WHERE user_id={userId}")
            history = cursor.fetchall()

            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return {"message": "Something went wrong"}
        finally:
            if(connection is not None):
                connection.close()
            return history

    # Adds a new User to the database
    @classmethod
    def registration(cls, username: str, password: str):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT * FROM UserTable WHERE username={username}") # TODO
            row = cursor.fetchone()
            if(row is not None):
                return {"Error": "Unable to create new user: Duplicate username"}   # TODO

            hashedPassword, salt = hash(password)

            cursor.execute(f"INSERT INTO UserTable(username) VALUES({username})")
            cursor.execute(f"INSERT INTO LoginData(user_id, password, salt) VALUES((SELECT id WHERE username={username}), {hashedPassword}, {salt})")

            connection.commit()
            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return {"Error": "Unable to create new user"}   # TODO
        finally:
            if(connection is not None):
                connection.close()
            return {"message": "Registration successful"}   # TODO

    # Marks existing user as archived
    @classmethod
    def archive(cls, userId: int):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT * FROM UserTable WHERE id={userId}")
            row = cursor.fetchone()
            if(row is not None):
                return {"Error": "Unable to archive user: does note exist"} #TODO

            cursor.execute(f"UPDATE UserData SET archived=TRUE WHERE id={userID}")

            connection.commit()
            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return {"Error": "Unable to archive user"}  #TODO
        finally:
            if(connection is not None):
                connection.close()
                return {"message": "User successfully archived"}    # TODO

    # secure password with sha512
    def __hash(self, password: str):
        salt = hashlib.sha512(os.urandom(60)).hexdigest().encode("ascii")
        hashedValue = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 10000)

        return (salt + binascii.hexlify(hashedValue)), salt

    @classmethod
    def login(cls, username: str, password: str):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM UserTable WHERE username={username}")
            row = cursor.fetchone()
            if(row is None):
                return False

            if(validateLogin(User(username), row[0], password)):
                return True
        except mysql.DatabaseError as error:
            print(error)
            return False

    @classmethod
    def validateLogin(cls, user: User, userId: str, password: str):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            # get the salt and password
            cursor.execute("SELECT password, salt FROM LoginData WHERE user_id = {userId}")
            row = cursor.fetchone()

            dbPassword = row[0]
            salt = row[1]

            if(password == salt + dbPassword):
                user.authenticate()
                return True

            return False
        except mysql.DatabaseError as error:
            print(error)
            return False

    @classmethod
    def logout(cls, user: User, tokenId: str):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT * FROM RevokedTokens WHERE id={tokenId}")
            row = cursor.fetchone()
            if(row is None):
                return False

            cursor.execute(f"INSERT INTO RevokedTokens(jti) VALUES({tokenId})")

            connection.commit()
            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return False
        finally:
            if(connection is not None):
                connection.close()
            return True

    @classmethod
    def tokenIsBlacklisted(cls, jti: str):
        connection = None
        try:
            connection = mysql.connector.connect(cls.CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"SELECT * FROM RevokedTokens WHERE jti={jti}")
            row = cursor.fetchone()

            if(row is not None):
                return True

            cursor.close()
        except mysql.DatabaseError as error:
            print(error)
            return True
        finally:
            if(connection is not None):
                connection.close()
            return False
