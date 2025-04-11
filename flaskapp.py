from flask import Flask, render_template, request, redirect, url_for, flash, session
from botocore.exceptions import ClientError
import boto3
import pymysql
import creds

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Setup DynamoDB
user_table = boto3.resource('dynamodb', region_name='us-east-1').Table('UserAccountsPoems')

# SQL connection setup
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

# Route: Home
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        rows = execute_query("SELECT * FROM Poems")
        html = """
        <html><body>
        <h2>Poems Table</h2>
        <a href='/add_poem'>Add New Poem</a><br><br>
        <table border='1' cellpadding='5'>
        <tr><th>PoemID</th><th>Title</th><th>Text</th><th>AuthorUserName</th></tr>
        """
        for r in rows:
            html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
        html += "</table></body></html>"
        return html
    except Exception as e:
        return f"<h3>Error: {e}</h3>"

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Get current max ID
        users = user_table.scan()['Items']
        max_id = max([u.get('UserIDNums', 0) for u in users], default=0)

        user_item = {
            'UserName': username,
            'Password': password,
            'Comments': [],
            'Poems': [],
            'UserIDNums': max_id + 1
        }
        user_table.put_item(Item=user_item)
        flash('Account created! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = user_table.get_item(Key={'UserName': username})
        user = response.get('Item')

        if user and user['Password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Login failed!')
    return render_template('login.html')

# Route: Add Poem
@app.route('/add_poem', methods=['GET', 'POST'])
def add_poem():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        author = session['username']

        rows = execute_query("SELECT MAX(PoemID) FROM Poems")
        max_id = rows[0][0] if rows[0][0] is not None else 0
        new_id = max_id + 1

        execute_insert(
            "INSERT INTO Poems (PoemID, Title, Text, AuthorUserName) VALUES (%s, %s, %s, %s)",
            (new_id, title, text, author)
        )
        flash('Poem added!')
        return redirect(url_for('index'))
    return render_template('add_poem.html')

if __name__ == '__main__':
    app.run(debug=True)
