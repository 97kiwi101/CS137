# auth.py
from flask import render_template, request, redirect, url_for, flash, session
from dbCode import user_table

def register_user():#ChatGpt
    '''
    It request an input for the user then it is inputed into the dynamo db. The user is assigned a userid number that is unique and so its easier for users to access the account 
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
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
        except Exception as e:
            flash(f"Error during registration: {e}")
    return render_template('register.html')

def authenticate_user():#ChatGpt
    '''
    gets the name and password of the user then its checked to see if its true or not.
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            response = user_table.get_item(Key={'UserName': username})
            user = response.get('Item')

            if user and user['Password'] == password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Login failed! Check credentials.')
        except Exception as e:
            flash(f"Login error: {e}")
    return render_template('login.html')
