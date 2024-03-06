# Imports
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from datetime import datetime, timedelta
import website.db_connect as db_connect
import mysql.connector, bcrypt
from functools import wraps

# Create a Blueprint for the authentication routes
config = db_connect.connect_to_database()
auth = Blueprint('auth', __name__)


# Route for admin login
@auth.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        connect = mysql.connector.connect(**config)
        cursor = connect.cursor()

        # Query to fetch admin user data by email
        query = "SELECT id, password, firstname FROM admin_users WHERE email = %s;"
        param = (email,)
        cursor.execute(query, param)
        user = cursor.fetchone()
        connect.close()
        
        if user is not None:
            user_id, hashed_password, firstname = user
            
             # Check if the entered password matches the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                
                # Store user information in the session
                session['user_id'] = user_id
                session['email'] = email
                
                flash("Je bent ingelogd!", "succes")
                return redirect(url_for('auth.admin_panel'))

            else:
                flash('Deze E-mail en wachtwoord combinatie is onjuist', 'danger')
        else:
            flash('Deze E-mail en wachtwoord combinatie is onjuist', 'danger')
            
    return render_template('admin_login.html')


# Route for logging out
@auth.route('/logout')
def logout():
    if 'email' in session:
        session.clear()
        flash('Je bent uccesvol uitgelogd!', 'succes')
    return redirect(url_for('auth.admin_login'))


# Route for admin panel
@auth.route('/admin_panel')
def admin_panel():
    if 'email' not in session:
        return redirect(url_for('auth.admin_login'))
    
    # Connect to the database
    connect = mysql.connector.connect(**config)
    cursor = connect.cursor()

     # Query to fetch data from fs_users table
    query = "SELECT id, firstname, prefix, lastname, email, ip_addr FROM fs_users;"
    cursor.execute(query)
    ip_users = cursor.fetchall()
    connect.close()

    return render_template('admin_panel.html', ip_users=ip_users)


# Route for creating a new user with the IP
@auth.route('/create-ip-user', methods=['POST'])
def create_ip_user():
    if 'email' not in session:
        return redirect(url_for('auth.admin_login'))

    # Get data from the html form
    firstname = request.form.get('firstname')
    prefix = request.form.get('prefix')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    ip = request.form.get('ip')

    # Connect to the database
    connect = mysql.connector.connect(**config)
    cursor = connect.cursor()

    # Query to insert a new user into fs_users table
    query = "INSERT INTO fs_users (firstname, prefix, lastname, email, ip_addr) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(query, (firstname, prefix, lastname, email, ip))

    connect.commit()
    connect.close()

    flash('New User IP created successfully', 'success')
    return redirect(url_for('auth.admin_panel'))


# Route for deleting an IP user
@auth.route('/delete-ip-user/<int:user_id>')
def delete_ip_user(user_id):
    if 'email' not in session:
        return redirect(url_for('auth.admin_login'))

    # Connect to the database
    connect = mysql.connector.connect(**config)
    cursor = connect.cursor()

    # Query to delete a user by user_id
    query = "DELETE FROM fs_users WHERE id = %s;"
    cursor.execute(query, (user_id,))

    connect.commit()
    connect.close()

    flash('User successfully deleted', 'success')
    return redirect(url_for('auth.admin_panel'))


# Route for editing an IP user
@auth.route('/edit-ip-user/<int:user_id>')
def edit_ip_user(user_id):
    if 'email' not in session:
        return redirect(url_for('auth.admin_login'))

    # Connect to the database
    connect = mysql.connector.connect(**config)
    cursor = connect.cursor()

    # Query to fetch user data by user_id
    query = "SELECT id, firstname, prefix, lastname, email, ip_addr FROM fs_users WHERE id = %s;"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()

    connect.close()

    if user_data is None:
        flash('User not found', 'danger')
        return redirect(url_for('auth.admin_panel'))

    return render_template('edit_user.html', user=user_data)

# Route for updating an IP user
@auth.route('/update-ip-user/<int:user_id>', methods=['POST'])
def update_ip_user(user_id):
    if 'email' not in session:
        return redirect(url_for('auth.admin_login'))

    # Get data from the html form
    firstname = request.form['firstname']
    prefix = request.form['prefix']
    lastname = request.form['lastname']
    email = request.form['email']
    ip = request.form['ip']

    # Connect to the database
    connect = mysql.connector.connect(**config)
    cursor = connect.cursor()

     # Query to update user data by user_id
    query = "UPDATE fs_users SET firstname=%s, prefix=%s, lastname=%s, email=%s, ip_addr=%s WHERE id=%s;"
    cursor.execute(query, (firstname, prefix, lastname, email, ip, user_id))

    connect.commit()
    connect.close()

    flash('User successfully updated', 'success')
    return redirect(url_for('auth.admin_panel'))


# Function to check if an IP address is whitelisted
def ip_whitelist(ip_address):
    # Connect to the database
    connect = mysql.connector.connect(**config)
    cursor = connect.cursor()

    try:
        # SQL query to count IP address in the database
        query = "SELECT COUNT(1) FROM fs_users WHERE ip_addr = %s;"
        cursor.execute(query, (ip_address,))

        # Fetch the result which is a tuple
        result = cursor.fetchone()

        # Check if the count is more than 0, if more than 1 IP address is whitelisted
        return result[0] > 0
    
    # Handle any exceptions with the MySQL database such as connection issues or SQL error
    except mysql.connector.Error as err:
        print(f"Error: {err}")

         # Return False to show that the IP address is not whitelisted beacause of the error
        return False
    
    # Close the cursor and the database connection 
    finally:
        cursor.close()
        connect.close()

# Function to get the client's IP address from the request
def get_client_ip(request):
    ip = request.remote_addr
    return ip

# Decorator function to check if the client's IP is whitelisted
def check_ip(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        visitor_ip = get_client_ip(request)
        if not ip_whitelist(visitor_ip):
            return redirect(url_for('auth.location_error'))
        return func(*args, **kwargs)
    return decorated_function


# Route for the home page, with IP whitelist check
@auth.route('/')
@check_ip
def home():
    return render_template('Flexservice.html')

# Route for displaying a location error page when ip is not in whitelist
@auth.route('/error')
def location_error():
    return render_template('location_error.html')


@auth.route('/ip_addr')
def index():
    user_ip = request.remote_addr
    return f"Your IP: {user_ip}"