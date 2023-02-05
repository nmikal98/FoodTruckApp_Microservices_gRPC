from audioop import add
import logging
from elasticsearch import Elasticsearch, exceptions
import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, after_this_request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import bcrypt
import sys
import requests
import json
from flask_cors import CORS
from extract import json_extract
import os
import re
import datetime

#es = Elasticsearch("http://localhost:9200")

es = Elasticsearch(host='es')

app = Flask(__name__)
CORS(app)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'SBKx2OPukLUp3xZ0kF2og3hcGv2Jyuth'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'mydb'
#app.config['MYSQL_HOST'] = 'host.docker.internal'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aa123456!'
app.config['MYSQL_DB'] = 'foodtruckdb'

# Intialize MySQL
mysql = MySQL(app)


################################################
# ElasticSearch Functions
################################################


def load_data_in_es():
    """ creates an index in elasticsearch """
    url = "http://data.sfgov.org/resource/rqzj-sfat.json"
    r = requests.get(url)
    data = r.json()
    print("Loading data in elasticsearch ...")
    for id, truck in enumerate(data):
        res = es.index(index="sfdata", id=id, document=truck)
    print("Total trucks loaded: ", len(data))


def safe_check_index(index, retry=3):
    """ connect to ES with retry """
    if not retry:
        print("Out of retries. Bailing out...")
        sys.exit(1)
    try:
        status = es.indices.exists(index=index)
        return status
    except exceptions.ConnectionError as e:
        print("Unable to connect to ES. Retrying in 5 secs...")
        time.sleep(5)
        safe_check_index(index, retry-1)


def format_fooditems(string):
    items = [x.strip().lower() for x in string.split(":")]
    return items[1:] if items[0].find("cold truck") > -1 else items


def check_and_load_index():
    """ checks if index exits and loads the data accordingly """
    if not safe_check_index('sfdata'):
        print("Index not found...")
        load_data_in_es()

################################################
# APP
################################################


@app.route("/")
def index():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    return render_template('index.html')


@app.route('/debug')
def test_es():
    resp = {}
    try:
        msg = es.cat.indices()
        resp["msg"] = msg
        resp["status"] = "success"
    except:
        resp["status"] = "failure"
        resp["msg"] = "Unable to reach ES"
    return jsonify(resp)


@app.route('/search')
def search():
    key = request.args.get('q')
    if not key:
        return jsonify({
            "status": "failure",
            "msg": "Please provide a query"
        })
    try:
        res = es.search(
            index="sfdata",
            body={
                "query": {"match": {"fooditems": key}},
                "size": 750  # max document size
            })
    except Exception as e:
        return jsonify({
            "status": "failure",
            "msg": "error in reaching elasticsearch"
        })
    # filtering results
    vendors = set([x["_source"]["applicant"] for x in res["hits"]["hits"]])
    temp = {v: [] for v in vendors}
    fooditems = {v: "" for v in vendors}
    for r in res["hits"]["hits"]:
        applicant = r["_source"]["applicant"]
        if "location" in r["_source"]:
            truck = {
                "hours": r["_source"].get("dayshours", "NA"),
                "schedule": r["_source"].get("schedule", "NA"),
                "address": r["_source"].get("address", "NA"),
                "location": r["_source"]["location"]
            }
            fooditems[applicant] = r["_source"]["fooditems"]
            temp[applicant].append(truck)

    # building up results
    results = {"trucks": []}
    for v in temp:
        results["trucks"].append({
            "name": v,
            "fooditems": format_fooditems(fooditems[v]),
            "branches": temp[v],
            "drinks": fooditems[v].find("COLD TRUCK") > -1
        })
    hits = len(results["trucks"])
    locations = sum([len(r["branches"]) for r in results["trucks"]])

    return jsonify({
        "trucks": results["trucks"],
        "hits": hits,
        "locations": locations,
        "status": "success"
    })


@app.route('/searchstore')
def searchstore():
    key = request.args.get('q')
    if not key:
        return jsonify({
            "status": "failure",
            "msg": "Please provide a query"
        })
    try:
        res = es.search(
            index="sfdata",
            body={
                "query": {"match_phrase": {"applicant": key}},
                "size": 750  # max document size
            }
        )
    except Exception as e:
        return jsonify({
            "status": "failure",
            "msg": "error in reaching elasticsearch"
        })
    # filtering results
    vendors = set([x["_source"]["applicant"] for x in res["hits"]["hits"]])
    temp = {v: [] for v in vendors}
    fooditems = {v: "" for v in vendors}
    for r in res["hits"]["hits"]:
        applicant = r["_source"]["applicant"]
        if "location" in r["_source"]:
            truck = {

                "address": r["_source"].get("address", "NA")
            }
            fooditems[applicant] = r["_source"]["fooditems"]
            temp[applicant].append(truck)

    # building up results
    results = {"trucks": []}
    for v in temp:
        results["trucks"].append({
            "name": v,
            "fooditems": format_fooditems(fooditems[v]),
            "branches": temp[v],
            "drinks": fooditems[v].find("COLD TRUCK") > -1
        })
    hits = len(results["trucks"])
    locations = sum([len(r["branches"]) for r in results["trucks"]])

    return jsonify({
        "trucks": results["trucks"]
    })

# http://localhost:5000/login - the following will be our login page, which will use both GET and POST requests


@app.route("/login", methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s ', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in our database
        if account:
            storedpsw = account['userPsw'].encode('utf-8')
            # check if the passeword is correct
            if bcrypt.checkpw(password, storedpsw):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Incorrect password
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist
            msg = 'Incorrect username!'

    return render_template('login.html', msg='')


# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('index'))


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
        email = request.form['email']
        phoneNum = request.form['phone_number']
        deliveryAddr = request.form['delivery_address']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not phoneNum or not deliveryAddr:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, %s, %s, %s,%s ,%s)', (username, hashedPassword, email, phoneNum, deliveryAddr))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/myOrders')
def myOrders():
    # Check if user is loggedin
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM orders WHERE userid = %s',
                       (session['id'],))
        data = cursor.fetchall()

        print(data)

        return render_template('myOrders.html', data=data)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# @app.route('/truck/saveinfo', methods=['GET', 'POST'])
# def truckinfo():

#     if request.method == 'POST':

#         data = request.get_json()

#         name = json_extract(data, 'name')
#         slocations = ','.join(json_extract(data, 'address'))
#         smenu = ','.join(data['data']['fooditems'])

#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM foodtruck WHERE truckname = %s', (name))

#         if (cursor.rowcount == 0):
#             cursor.execute(
#                 'INSERT INTO foodtruck VALUES (NULL, %s, %s, %s)', (name, slocations, smenu))
#             mysql.connection.commit()

#         return '', 200


@app.route('/placeOrder', methods=['GET', 'POST'])
def placeOrder():

    if 'loggedin' in session:

        # Show the profile page with account info
        # , locations=locations, menu=menu

        name = request.args.get('key')

        if not name:
            return jsonify({
                "status": "failure",
                "msg": "Please provide a query"
            })

        res = requests.get('http://localhost:5000/searchstore?q="'+name+'"')
        truck_data = res.json()

        locations = []

        for item in truck_data['trucks'][0]['branches']:
            for attr, val in item.items():
                locations.append(val)

        menu = truck_data['trucks'][0]['fooditems']

        # response = requests.request(
        #     method="POST", url='/searchstore', data=name)

        # print(response)
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute(
    #         'SELECT * FROM foodtruck WHERE truckname = %s', [name])
    #     truck = cursor.fetchone()

    #     locations = re.split('[,&]', truck['locations'])
    #     menu = re.split('[,&]', truck['menu'])

        return render_template('order.html', name=name, locations=locations, menu=menu)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/cancel')
def cancel():

    return redirect(url_for('index'))


@app.route('/saveOrder', methods=['POST'])
def saveOrder():

    if 'loggedin' in session:

        try:
            if request.method == 'POST':

                name = request.args.get('name')
                loc = request.args.get('location')
                items = request.args.get('items')

                if not name:
                    orderDetails = ""
                    itterations = 0
                    truckname = request.form['truckname']

                    location = request.form['location']

                    for item, itemQuantity in zip(request.form.getlist('item'), request.form.getlist('itemQuantity')):

                        if itemQuantity != '0':
                            if itterations == 0:
                                orderDetails = item + ":" + itemQuantity
                                itterations += 1
                            else:
                                orderDetails = orderDetails + "," + \
                                    item + ":" + itemQuantity
                else:
                    truckname = name
                    location = loc
                    orderDetails = items

                res = requests.get(
                    'http://localhost:5000/searchstore?q="'+truckname+'"')
                truck_data = res.json()

                if truck_data['trucks'] != []:

                    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    cursor = mysql.connection.cursor(
                        MySQLdb.cursors.DictCursor)

                    cursor.execute(
                        'INSERT INTO orders VALUES (NULL, %s, %s, %s,%s, %s)', (session['id'], truckname, location, orderDetails, date))
                    mysql.connection.commit()
                else:
                    print("Foodtruck not found")
                    redirect(url_for('home'))

            else:
                redirect(url_for('home'))
        except Exception as e:
            print(str(e))

        return redirect(url_for('myOrders'))
 # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    check_and_load_index()
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)
