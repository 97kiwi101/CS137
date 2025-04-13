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


'''
Basic intro funtions 
'''
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Get all poems
        poems = execute_query("SELECT * FROM Poems ORDER BY PoemID DESC")

        # Get all comments (now including CommentID)
        comment_rows = execute_query("SELECT CommentID, PoemID, CommentText, CommenterUserName FROM Comments")
        comments_by_poem = {}

        for row in comment_rows:
            comment_id = row[0]
            poem_id = row[1]
            comment = {
                'id': comment_id,
                'comment': row[2],
                'username': row[3]
            }
            if poem_id not in comments_by_poem:
                comments_by_poem[poem_id] = []
            comments_by_poem[poem_id].append(comment)

        return render_template('index.html', poems=poems, comments=comments_by_poem)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"

@app.route('/register', methods=['GET', 'POST']) #ChatGpt
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

@app.route('/login', methods=['GET', 'POST']) #ChatGpt
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


'''
Comments effects
'''
@app.route('/add_comment/<int:poem_id>', methods=['POST'])
def add_comment(poem_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    comment_text = request.form['comment_text']
    username = session['username']

    try:
        # Insert comment into SQL table
        execute_insert(
            "INSERT INTO Comments (PoemID, CommentText, CommenterUserName) VALUES (%s, %s, %s)",
            (poem_id, comment_text, username)
        )

        # Optional: Also store in DynamoDB if needed
        response = user_table.get_item(Key={'UserName': username})
        user = response.get('Item')

        if user:
            new_comment = {
                'PoemID': poem_id,
                'Text': comment_text
            }
            updated_comments = list(user.get('Comments', []))
            updated_comments.append(new_comment)

            user_table.update_item(
                Key={'UserName': username},
                UpdateExpression="SET Comments = :c",
                ExpressionAttributeValues={':c': updated_comments}
            )

        flash('Comment added!')

    except Exception as e:
        flash(f"Error adding comment: {e}")

    return redirect(url_for('index'))

@app.route('/delete_comment/<int:poem_id>', methods=['POST'])
def delete_comment(poem_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    comment_text = request.form['comment_text']

    # Delete the exact comment
    execute_insert(
        "DELETE FROM Comments WHERE PoemID = %s AND CommenterUserName = %s AND CommentText = %s",
        (poem_id, username, comment_text)
    )

    flash('Comment deleted.')
    return redirect(url_for('index'))

@app.route('/delete_comment_by_id/<int:comment_id>', methods=['POST'])
def delete_comment_by_id(comment_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Only allow user to delete their own comment
    row = execute_query("SELECT CommenterUserName FROM Comments WHERE CommentID = %s", (comment_id,))
    if row and row[0][0] == username:
        execute_insert("DELETE FROM Comments WHERE CommentID = %s", (comment_id,))
        flash("Comment deleted.")
    else:
        flash("You can only delete your own comments.")

    return redirect(url_for('index'))


'''
Poem effects
'''
@app.route('/add_poem', methods=['GET', 'POST'])#ChatGpt
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

@app.route('/delete_poem/<int:poem_id>', methods=['POST'])
def delete_poem(poem_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    author = session['username']
    poem = execute_query("SELECT AuthorUserName FROM Poems WHERE PoemID = %s", (poem_id,))

    if poem and poem[0][0] == author:
        # Delete poem and its comments
        execute_insert("DELETE FROM Comments WHERE PoemID = %s AND CommenterUserName = %s", (poem_id, author))
        execute_insert("DELETE FROM Poems WHERE PoemID = %s", (poem_id,))
        flash('Poem deleted successfully.')
    else:
        flash('You can only delete your own poems.')

    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
