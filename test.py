import pymysql
import creds

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user,
        password= creds.password,
        db=creds.db,
        )
    cur = conn.cursor()

try:
    get_conn()
    print("IT FUCKING WORKS")
except Exception as e:
    print("Failed to connect:", e)
