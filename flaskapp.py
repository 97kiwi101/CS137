from flask import Flask, render_template
import mysql.connector
from creds import db_config

app = Flask(__name__)

@app.route('/')
def index():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM ProjectOnePoems")
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('index.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
