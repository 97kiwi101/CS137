# dbCode.py
import pymysql
import boto3
import creds

# Setup DynamoDB
user_table = boto3.resource('dynamodb', region_name='us-east-1').Table('UserAccountsPoems')

def get_conn():
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db
    )

def execute_query(query, args=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute_insert(query, args=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()
    conn.close()
