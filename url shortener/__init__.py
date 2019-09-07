from flask import Flask,render_template, request, url_for, session, redirect, jsonify
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime
import requests
import sqlite3
from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import base64
import re
try:
    from urllib.parse import urlparse  # Python 3
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse  # Python 2
    str_encode = str
try:
    from string import ascii_lowercase
    from string import ascii_uppercase
except ImportError:
    from string import lowercase as ascii_lowercase
    from string import uppercase as ascii_uppercase
import base64

def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INT PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


def toBase62(num, b=62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + ascii_lowercase + ascii_uppercase
    r = num % b
    res = base[r]
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def toBase10(num, b=62):
    base = string.digits + ascii_lowercase + ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res



# Assuming urls.db is in your app root folder
app = Flask(__name__)
host = 'http://localhost:5000/'
app = Flask(__name__)

s = URLSafeTimedSerializer('Thisisasecret!')

app.config['SECRET_KEY'] = 'secret'

conn = sqlite3.connect("data.db")
c = conn.cursor()

def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS users (id integer primary key autoincrement, name text, email text, mobile text, password text)")
	
create_table()
conn.commit()
conn.close()


@app.route('/',methods=['POST','GET'])
def index():
	if request.method == 'POST':
		try:
			if request.form['test'] == 'login':
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				email = request.form['lemail']
				c.execute("SELECT * FROM users WHERE email=?",(email,))
				user = c.fetchone()
				conn.commit()
				conn.close()
				if user:
					if user[4] == request.form['lpass']:
						session['username'] = str(email)
						return redirect(url_for('dash'))
					return render_template('index.html',msg='wrong')
				return render_template('index.html',msg='wrong')
			elif request.form['test'] == 'signup':
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				names = request.form['name']
				email = request.form['semail']
				mobile = request.form['mobile']
				spass = request.form['spass']
				c.execute("SELECT * FROM users WHERE email=?",(email,))
				data = c.fetchone()
				if data:
					msg = 'warning'
					return render_template('index.html', msg=msg)
				else:
					c.execute("INSERT INTO users(name, email, mobile, password) VALUES(?,?,?,?)",(names, email, mobile, spass))
				conn.commit()
				conn.close()
			return render_template('index.html', msg='success')
		except Exception as e:
			return str(e)
			return render_template('hidden.html')
	return render_template('index.html')

@app.route('/dash',methods=['POST','GET'])
def dash():
	if request.method == 'POST':
		original_url = str_encode(request.form.get('url'))
		if urlparse(original_url).scheme == '':
			url = 'http://' + original_url
		else:
			url = original_url
		with sqlite3.connect('urls.db') as conn:
			cursor = conn.cursor()
			res = cursor.execute(
				'INSERT INTO WEB_URL (URL) VALUES (?)',
				[base64.urlsafe_b64encode(url)]
			)
			encoded_string = toBase62(res.lastrowid)
		return render_template('dashboard.html', short_url=host + encoded_string)
	return render_template('dashboard.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded = toBase10(short_url)
    url = host  # fallback if no URL is found
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as e:
            print(e)
    return redirect(url)

@app.route('/prof/<link>')
def profile(link):
	try:
		url = request.url_root + link
		l = s.loads(link)
		conn = sqlite3.connect("data.db")
		c = conn.cursor()
		c.execute("SELECT * FROM users WHERE email=?",(l,))
		new_id = c.fetchone()
		c.execute("SELECT * FROM details WHERE f_id=?",(new_id[0],))
		data = c.fetchone()
		name = new_id[1]
		email = new_id[2]
		mob = new_id[3]
		git = ""
		photo =""
		ab = ""
		privateBool = 0
		if data:
			git = data[2]
			photo = data[3]
			ab = data[4]
			privateBool = data[6]
		if privateBool == 0:
			return render_template('dashboard.html',ab=ab,privateBool=privateBool,url=url,photo=photo,name=name, git=git, mob=mob,email=email)
		return render_template('hidden.html')
	except Exception as e:
		return str(e)
		return render_template('hidden.html')

@app.route('/search',methods=['POST'])
def search():
	if request.method == 'POST':
		n = request.form['n']
		a = re.compile(str(request.form['n']), re.IGNORECASE)
		doc = []
		details = []
		url = request.url_root + 'prof/'
		conn = sqlite3.connect("data.db")
		c = conn.cursor()
		c.execute("SELECT * FROM users")
		z = c.fetchall()
		for i in z:
			b = a.findall(i[1])
			for j in b:
				c.execute("SELECT * FROM details WHERE f_id=?",(i[0],))
				h = c.fetchone()
				if i not in doc:
					doc.append(i)
					details.append(h)
		return render_template('s.html',doc=doc,details=details,url=url)

@app.route('/timeline/', methods=['POST','GET'])
def timel():
	if session['username']:
		try:
			response = requests.get("http://127.0.0.1:8000/")
			r = response.json()
			posts = r['timeline']
			if request.method == 'POST':
				user_email = session['username']
				img = request.files['chooseFile']
				if img:
					file = img.read()
					b64 = base64.b64encode(file)
					picc = b64.decode('utf-8')
					if picc[0] == '/':
						pic = picc[1:]
					else:
						pic = picc
				else:
					pic = "0"
				text = '.'
				if request.form['data']:
					text = request.form['data']
				response = requests.post(f"http://127.0.0.1:8000/{user_email}/img&{pic}/{text}")
				return redirect(url_for('timel'))
			return render_template('timeline.html',posts=posts)
		except Exception as e:
			return str(e)
			return render_template('hidden.html')
	return redirect(url_for('index'))

@app.route('/delete')
def delete():
	if session['username']:
		try:
			conn = sqlite3.connect("data.db")
			c = conn.cursor()
			c.execute("DELETE FROM users WHERE email=?",(session['username'],))
			conn.commit()
			conn.close()
			session['username'] = None
			return redirect(url_for('index'))
		except:
			return render_template('hidden.html')
	return redirect(url_for('index'))

@app.route('/logout')
def log():
	if session['username']:
		session['username'] = None
		return redirect(url_for('index'))
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)