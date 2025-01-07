import mysql.connector as connector
from mysql.connector import Error
import os

class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Establish a connection to the database."""
        try:
            self.connection = connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connection to the database was successful.")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

class QueryExecutor:
    def __init__(self, connection):
        self.connection = connection

    def run_query_from_file(self, file_path):
        """Run an SQL query from the provided file path."""
        if not self.connection or not self.connection.is_connected():
            return "No active database connection."

        try:
            with open(file_path, 'r') as file:
                sql_query = file.read()

            cursor = self.connection.cursor()
            cursor.execute(sql_query)

            results = cursor.fetchall()

            output = [row for row in results]

            cursor.close()
            return output
        except Error as e:
            return f"Error executing query: {e}"
