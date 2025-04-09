import mysql.connector
from creds import db_config

try:
    conn = mysql.connector.connect(**db_config)
    print("Connected!")
except Exception as e:
    print("Failed to connect:", e)
