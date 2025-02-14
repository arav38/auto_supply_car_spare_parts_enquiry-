import os
import pyodbc
from flask import Flask, render_template, redirect, url_for, request, flash
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
    conn = pyodbc.connect(
        f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
    )
    return conn

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Customer Login Route
@app.route('/customer_login')
def customer_login():
    return render_template('customer_login.html')

# Supplier Login Route
@app.route('/supplier_login')
def supplier_login():
    return render_template('supplier_login.html')

# Signup Route (Inserts Data into SQL Server)
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    name = request.form['name']
    email = request.form['email']
    contact_number = request.form['contact_number']

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the username or email already exists
    cursor.execute("SELECT * FROM Users WHERE Username = ? OR EmailAddress = ?", (username, email))
    existing_user = cursor.fetchone()

    if existing_user:
        flash('Username or Email already exists. Try a different one.')
        conn.close()
        return redirect(url_for('home'))

    # Insert new user into the database
    cursor.execute(
        "INSERT INTO Users (Username, Password, Role, FullName, EmailAddress, ContactNumber) VALUES (?, ?, ?, ?, ?, ?)",
        (username, hashed_password, role, name, email, contact_number)
    )
    conn.commit()
    conn.close()

    flash('Signup successful! You can now log in.')
    return redirect(url_for('home'))

# Image Upload & WhatsApp Integration
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        image = request.files.get('image')
        message = request.form.get('message')

        if image:
            # Secure and save the file
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)

            # Send WhatsApp message with Twilio
            send_whatsapp_message(message)

            flash(f"Image uploaded and message sent: {message}")
            return redirect(url_for('upload_image'))

    return render_template('upload_image.html')

# Function to Send WhatsApp Messages via Twilio
def send_whatsapp_message(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    
    recipient_number = 'whatsapp:+1234567890'  # Replace with recipient's WhatsApp number
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=recipient_number
    )

if __name__ == '__main__':
    app.run(debug=True)
