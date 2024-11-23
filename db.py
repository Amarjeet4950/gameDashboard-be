import psycopg2
from psycopg2 import sql
import threading

# Database connection parameters
HOST = "postgres"  # or IP address of the PostgreSQL server
PORT = "5432"  # Default PostgreSQL port
USER = "myuser"  # Your PostgreSQL username
PASSWORD = "mypassword"  # Your PostgreSQL password
DATABASE = "mydatabase"  # The name of your database

def get_conn():
    connection = psycopg2.connect(
                            host=HOST,
                            port=PORT,
                            user=USER,
                            password=PASSWORD,
                            database=DATABASE
                        )
    return connection

