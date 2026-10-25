import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="sarthak.1251070865",
        database="autonorm_db"
    )

    print("MySQL Connection Successful!")

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM project_test")
    print(cursor.fetchall())

    cursor.close()
    connection.close()

except Error as error:
    print("ACTUAL ERROR:", repr(error))