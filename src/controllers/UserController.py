import pyscopg2 as psycopg

from src.models.User import Users

class UserController:

    # TODO - turn into env variable
    CONN_STRING="host='localhost' dbname='stocksimulator' user='postgres' password=''"

    # Adds a new User to the database
    def add(self, userName: str, password: str):
        connection = None
        try:
            connection = psycopg.connect(CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"INSERT INTO UserTable(username) VALUES({userName})")
            cursor.execute(f"INSERT INTO LoginData(user_id, password) VALUES((SELECT id WHERE username={userName}), SHA256({password}))")
            
            connection.commit()
            cursor.close()
        except psycopg.DatabaseError as error:
            print(error)
        finally:
            if(connection is not None):
                connection.close()

    # Marks existing user as archived
    def archive(self, userId: int):
        connection = None
        try:
            connection = psycopg.connect(CONN_STRING)
            cursor = connection.cursor()

            cursor.execute(f"UPDATE UserData SET archived=TRUE WHERE id={userID}")

            connection.commit()
            cursor.close()
        except psycopg.DatabaseError as error:
            print(error)
        finally:
            if(connection is not None):
                connection.close()
