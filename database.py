import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="#your sql password here",
        database="digital_wallet_db"
    )

    return connection