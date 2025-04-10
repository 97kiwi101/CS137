# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT

from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from matplotlib import table
from botocore.exceptions import ClientError
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('UserAccountsPoems') 

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone

@app.route('/')
def home():
    try:
        response = table.scan()
        users_list = response.get('Items', [])
    except ClientError as e:
        flash(f"Error reading from DynamoDB: {e.response['Error']['Message']}", 'danger')
        users_list = []

    return render_template('display_users.html', users=users_list)



# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    