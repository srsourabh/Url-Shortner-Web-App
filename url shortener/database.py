from flask import Flask, url_for, redirect,jsonify
from datetime import datetime
import base64
import sqlite3
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'


@app.route('/',methods=['GET'])
def index():
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	c.execute("SELECT * FROM timeline ORDER BY id DESC ")
	a = c.fetchall()
	return jsonify({"timeline":a})

@app.route('/<string:email>/',methods=['POST'])
@app.route('/<string:email>/img&<path:img>/<string:text>',methods=['POST'])
def add(email, img=None, text=None):
	dateColumn = datetime.now().strftime("%B %d, %Y %I:%M%p")
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	c.execute("SELECT * FROM users WHERE email=?",(email,))
	result = c.fetchone()
	auth = result[1]
	conn.commit()
	conn.close()
	return jsonify({'success':'200'})


if __name__ == '__main__':
	app.run(debug=True,port=8000)