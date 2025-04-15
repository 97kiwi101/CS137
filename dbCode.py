import pymysql
import boto3
import creds

user_table = boto3.resource('dynamodb', region_name='us-east-1').Table('UserAccountsPoems')

def get_conn():
    '''
    gets the info form the creds file to have it sign in to the sql file
    '''
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db
    )

def execute_query(query, args=()):
    '''
    figures out the query request and does it
    '''
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute_insert(query, args=()):#ChatGpt
    '''
    adds things to the sql databases
    '''
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()
    conn.close()
