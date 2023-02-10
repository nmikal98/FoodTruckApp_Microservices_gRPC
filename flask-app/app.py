import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import bcrypt
from flask_cors import CORS
import datetime
import requests
from google.protobuf.json_format import MessageToDict

import order_pb2
import order_pb2_grpc 
import search_pb2
import search_pb2_grpc
import grpc

#es = Elasticsearch(host='es')

app = Flask(__name__)
CORS(app)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'SBKx2OPukLUp3xZ0kF2og3hcGv2Jyuth'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'mydb_micro'
#app.config['MYSQL_HOST'] = 'host.docker.internal'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aa123456!'
app.config['MYSQL_DB'] = 'foodtruckdb'

# Intialize MySQL
mysql = MySQL(app)





################################################
# APP
################################################


@app.route("/")
def index():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    return render_template('index.html')


@app.route('/search')
def search():
    key = request.args.get('q')

    if not key:
        return jsonify({
            "status": "failure",
            "msg": "Please provide a query"
        })
    
    with grpc.insecure_channel("host.docker.internal:9999") as channel:
        stub = search_pb2_grpc.searchServiceStub(channel)

        
        response = stub.Search(search_pb2.searchRequest(req=key))
        
        resp = jsonify(MessageToDict(response))
     

        return resp
            

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST': 

        return_template = True
        if 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
            username = request.form['username']
            password = request.form['password'].encode('utf-8')
        else:
            username = request.args.get('username')
            password = request.args.get('password')
            return_template = False


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

                if return_template:
                    return redirect(url_for('home'))
                else:
                    return request.cookies.get('session')
            else:
                # Incorrect password
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist
            msg = 'Incorrect username!'

    return render_template('login.html', msg='')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('index'))


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


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


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

        with grpc.insecure_channel("host.docker.internal:9999") as channel:
            stub = search_pb2_grpc.searchServiceStub(channel)

            response = stub.SearchStore(search_pb2.searchRequest(req=name))
            
        truck_data = MessageToDict(response)


        locations = []

        for item in truck_data['trucks'][0]['branches']:
            locations.append(item['address'])

        menu = truck_data['trucks'][0]['fooditems']

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


                with grpc.insecure_channel("host.docker.internal:9999") as channel:
                    stub = search_pb2_grpc.searchServiceStub(channel)
                    response = stub.SearchStore(search_pb2.searchRequest(req=truckname))
                    
                truck_data = MessageToDict(response)

                if truck_data['trucks'] != []:

                    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    with grpc.insecure_channel("host.docker.internal:9998") as channel:
                        stub = order_pb2_grpc.orderServiceStub(channel)
                        response = stub.order(order_pb2.orderRequest(sessId=session['id'], truckname=truckname, location=location, orderDetails=orderDetails, date=date))

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
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)
