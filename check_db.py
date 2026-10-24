from app.db import check_database_connection

if check_database_connection():
    print("Successfully connected to PostgreSQL!")