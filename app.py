import os
import pyodbc
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from twilio.rest import Client

app = Flask(__name__)

# Configuration for SQL Server
DB_SERVER = 'DESKTOP-GF47VQO'  # Change to your server name
DB_NAME = 'MyDatabase'  # Change to your database name
DB_USERNAME = 'Akshay'  # Your SQL username
DB_PASSWORD = '6644'  # Your SQL password
DB_DRIVER = '{ODBC Driver 17 for SQL Server}'

# Twilio Configuration
TWILIO_SID = 'your_account_sid'  # Replace with Twilio SID
TWILIO_AUTH_TOKEN = 'your_auth_token'  # Replace with Twilio Auth Token
TWILIO_PHONE_NUMBER = 'whatsapp:+14155238886'  # Twilio WhatsApp number

# Flask Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Database Connection Function
def get_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Customer Login Route
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():

    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Username, Password, Role FROM Users WHERE Username = ?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['role'] = user[2]
                flash('Login successful!')
                return redirect(url_for('upload_image'))
            else:
                flash('Invalid username or password!')
        else:
            flash("Database connection error!")

        return redirect(url_for('customer_login'))

    return render_template('customer_login.html')

# Supplier Login Route
@app.route('/supplier_login', methods=['GET', 'POST'])
def supplier_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT UserID,Username, Password, Role FROM Users WHERE Username = ?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['role'] = user[2]
                flash('Supplier login successful!')
                return redirect(url_for('upload_image'))
            else:
                flash('Invalid username or password!')
        else:
            flash("Database connection error!")

        return redirect(url_for('supplier_login'))

    return render_template('supplier_login.html')

# Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    name = request.form['name']
    email = request.form['email']
    contact_number = request.form['contact_number']

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ? OR EmailAddress = ?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username or Email already exists.')
            conn.close()
            return redirect(url_for('home'))

        cursor.execute(
            "INSERT INTO Users (Username, Password, Role, FullName, EmailAddress, ContactNumber) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hashed_password, role, name, email, contact_number)
        )
        conn.commit()
        conn.close()
        flash('Signup successful! You can now log in.')
    else:
        flash("Database connection error!")

    return redirect(url_for('home'))

# Image Upload & WhatsApp Integration
# Image Upload & Capture Integration
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if 'user_id' not in session:
        flash("You must be logged in to upload images!", "error")
        return redirect(url_for('customer_login'))

    if request.method == 'POST':
        image = request.files.get('image')  # Uploaded Image
        captured_image = request.form.get('captured_image')  # Captured Image (Base64)
        message = request.form.get('message')

        if not image and not captured_image:
            flash("Either upload an image or capture one!", "error")
            return redirect(url_for('upload_image'))

        if not message:
            flash("Message is required!", "error")
            return redirect(url_for('upload_image'))

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # If user uploaded an image file
            if image:
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)

                with open(filepath, 'rb') as file:
                    binary_data = file.read()

            # If user captured an image (Base64 format)
            elif captured_image:
                import base64
                binary_data = base64.b64decode(captured_image)
                filename = "captured_image.jpg"
            
            try:
                cursor.execute(
                    "INSERT INTO ClientUploads (client_id, image_data, image_name, message) VALUES (?, ?, ?, ?)",
                    (int(session['user_id']), binary_data, filename, message)
                )
                conn.commit()
                flash("Image uploaded and details saved successfully!", "success")
            except Exception as e:
                flash(f"Database error: {e}", "error")
            finally:
                conn.close()

            # Send WhatsApp message
            send_whatsapp_message(message)

        else:
            flash("Failed to connect to the database!", "error")

    return render_template('upload_image.html')


# Function to Send WhatsApp Messages via Twilio
def send_whatsapp_message(message):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        recipient_number = 'whatsapp:+1234567890'  # Replace with recipient's WhatsApp number

        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient_number
        )
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        flash("Failed to send WhatsApp message!", "error")

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
