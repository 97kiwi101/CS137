# flaskapp.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from auth import register_user, authenticate_user
from dbCode import execute_query, execute_insert, user_table

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    '''
    Checks if the user has a username if not its direacted to the login page. Then it will query the database to get strings and infomation that is later displayed
    '''
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        poems = execute_query("SELECT * FROM Poems ORDER BY PoemID DESC")
        comment_rows = execute_query("SELECT CommentID, PoemID, CommentText, CommenterUserName FROM Comments")

        comments_by_poem = {}
        for row in comment_rows:
            comment_id, poem_id, text, user = row
            comment = {'id': comment_id, 'comment': text, 'username': user}
            comments_by_poem.setdefault(poem_id, []).append(comment)

        return render_template('index.html', poems=poems, comments=comments_by_poem)
    except Exception as e:
        return f"<h3>Error: {e}</h3>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Calls register_user in auth.py
    '''
    return register_user()

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Calls authenticate_user() in auth.py
    '''
    return authenticate_user()

@app.route('/feedback')
def feedback():
    '''
    This is the join query requirment its used for the admin to have an over view of user behavoir
    '''
    query = """
    SELECT p.Title, c.CommentText, c.CommenterUserName
    FROM Poems p
    JOIN Comments c ON p.PoemID = c.PoemID
    ORDER BY p.PoemID DESC
    """
    results = execute_query(query)
    return render_template('feedback.html', results=results)


'''
Comments
'''
@app.route('/add_comment/<int:poem_id>', methods=['POST'])#ChatGpt
def add_comment(poem_id):
    '''
    Checks to see if the user is login before making a comment. Then it Will request and add the comment to the database for the index to be updated and seen then
    '''
    if 'username' not in session:
        return redirect(url_for('login'))

    comment_text = request.form['comment_text']
    username = session['username']

    try:
        execute_insert("INSERT INTO Comments (PoemID, CommentText, CommenterUserName) VALUES (%s, %s, %s)",
                       (poem_id, comment_text, username))

        user = user_table.get_item(Key={'UserName': username}).get('Item')
        if user:
            updated_comments = user.get('Comments', []) + [{'PoemID': poem_id, 'Text': comment_text}]
            user_table.update_item(
                Key={'UserName': username},
                UpdateExpression="SET Comments = :c",
                ExpressionAttributeValues={':c': updated_comments}
            )
        flash('Comment added!')
    except Exception as e:
        flash(f"Error adding comment: {e}")

    return redirect(url_for('index'))

@app.route('/delete_comment_by_id/<int:comment_id>', methods=['POST'])#ChatGpt
def delete_comment_by_id(comment_id):
    '''
    checks if user is in, then makes a query request to remove the users comment form the database. This is streamlined with comment ID
    '''
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    row = execute_query("SELECT CommenterUserName FROM Comments WHERE CommentID = %s", (comment_id,))
    if row and row[0][0] == username:
        execute_insert("DELETE FROM Comments WHERE CommentID = %s", (comment_id,))
        flash("Comment deleted.")
    else:
        flash("You can only delete your own comments.")
    return redirect(url_for('index'))

@app.route('/edit_comment/<int:comment_id>', methods=['POST'])#ChatGpt
def edit_comment(comment_id):
    '''
    Checks if the user is login. Then it will make a query request to edit and change the users coment text whiched is steamlined with comment id so the query can be easily located and singled out
    '''
    if 'username' not in session:
        return redirect(url_for('login'))

    new_text = request.form['new_comment_text']
    username = session['username']

    try:
        comment = execute_query("SELECT CommenterUserName FROM Comments WHERE CommentID = %s", (comment_id,))
        if comment and comment[0][0] == username:
            execute_insert("UPDATE Comments SET CommentText = %s WHERE CommentID = %s",
                           (new_text, comment_id))
            flash("Comment updated successfully.")
        else:
            flash("You can only edit your own comments.")
    except Exception as e:
        flash(f"Error updating comment: {e}")

    return redirect(url_for('index'))


'''
Poems
'''
@app.route('/add_poem', methods=['GET', 'POST'])#ChatGpt
def add_poem():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        author = session['username']

        new_id = execute_query("SELECT IFNULL(MAX(PoemID), 0) + 1 FROM Poems")[0][0]
        execute_insert("INSERT INTO Poems (PoemID, Title, Text, AuthorUserName) VALUES (%s, %s, %s, %s)",
                       (new_id, title, text, author))
        flash('Poem added!')
        return redirect(url_for('index'))
    return render_template('add_poem.html')

@app.route('/delete_poem/<int:poem_id>', methods=['POST'])#ChatGpt
def delete_poem(poem_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    author = session['username']
    poem = execute_query("SELECT AuthorUserName FROM Poems WHERE PoemID = %s", (poem_id,))
    if poem and poem[0][0] == author:
        execute_insert("DELETE FROM Comments WHERE PoemID = %s", (poem_id,))
        execute_insert("DELETE FROM Poems WHERE PoemID = %s", (poem_id,))
        flash('Poem deleted successfully.')
    else:
        flash('You can only delete your own poems.')

    return redirect(url_for('index'))

@app.route('/edit_poem/<int:poem_id>', methods=['GET', 'POST'])#ChatGpt
def edit_poem(poem_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    poem = execute_query("SELECT PoemID, Title, Text, AuthorUserName FROM Poems WHERE PoemID = %s", (poem_id,))

    if not poem or poem[0][3] != username:
        flash("You can only edit your own poems.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_title = request.form['title']
        new_text = request.form['text']
        execute_insert("UPDATE Poems SET Title = %s, Text = %s WHERE PoemID = %s",
                       (new_title, new_text, poem_id))
        flash("Poem updated successfully.")
        return redirect(url_for('index'))

    return render_template('edit_poem.html', poem=poem[0])


if __name__ == '__main__':
    app.run(debug=True)#this was changed through the nano on the EC2 so its a public setting
