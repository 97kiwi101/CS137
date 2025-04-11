# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT

from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from matplotlib import table
from botocore.exceptions import ClientError
import boto3
import pymysql
import creds

app = Flask(__name__)

def get_conn():
    conn = pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db
    )
    return conn

def execute_query(query, args=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def display_html(rows):
    html = """
    <html><body>
    <h2>Poems Table</h2>
    <table border="1" cellpadding="5">
    <tr><th>PoemID</th><th>Title</th><th>Text</th><th>AuthorUserName</th></tr>
    """
    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
    html += "</table></body></html>"
    return html

@app.route('/')
def index():
    try:
        rows = execute_query("SELECT * FROM Poems")
        return display_html(rows)
    except Exception as e:
        return f"<h3>Error: {e}</h3>"

if __name__ == '__main__':
    app.run(debug=True)