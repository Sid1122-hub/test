import pymysql
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "Siddharth1"  # Change to your password
DB_NAME = "users"

def get_db_connection():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        bank_account1_type = request.form.get('bank_account1_type', '')
        bank_account1_number = request.form.get('bank_account1_number', '')
        credit_card1 = request.form.get('credit_card1', '')
        
        bank_account2_type = request.form.get('bank_account2_type', '')
        bank_account2_number = request.form.get('bank_account2_number', '')
        credit_card2 = request.form.get('credit_card2', '')
        
        bank_account3_type = request.form.get('bank_account3_type', '')
        bank_account3_number = request.form.get('bank_account3_number', '')
        credit_card3 = request.form.get('credit_card3', '')

        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            query = f"""
            INSERT INTO user (username, email, password, 
            bank_account1_type, bank_account1_number, credit_card1, 
            bank_account2_type, bank_account2_number, credit_card2, 
            bank_account3_type, bank_account3_number, credit_card3)
            VALUES ('{username}', '{email}', '{password}', 
            '{bank_account1_type}', '{bank_account1_number}', '{credit_card1}',
            '{bank_account2_type}', '{bank_account2_number}', '{credit_card2}',
            '{bank_account3_type}', '{bank_account3_number}', '{credit_card3}')
            """
            cursor.execute(query)
            connection.commit()
            flash("User registered successfully!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # SQL Injection Vulnerability
            query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(query)
            user = cursor.fetchone()

            if user:
                session['user'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials!", "error")
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash("Session not found. Please login.", "error")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch user details
    query = f"SELECT * FROM user WHERE username = '{session['user']}'"
    cursor.execute(query)
    user = cursor.fetchone()

    filter_input = request.form.get('filter', '').strip()
    output = None
    filtered_accounts = []

    if filter_input:
        # Fetch all bank accounts from the user
        user_accounts = [
            {'type': user['bank_account1_type'], 'number': user['bank_account1_number'], 'credit_card': user['credit_card1']},
            {'type': user['bank_account2_type'], 'number': user['bank_account2_number'], 'credit_card': user['credit_card2']},
            {'type': user['bank_account3_type'], 'number': user['bank_account3_number'], 'credit_card': user['credit_card3']}
        ]

        # Filter only matching accounts
        filtered_accounts = [acc for acc in user_accounts if filter_input.lower() in acc['type'].lower()]

        # If no match, treat it as code injection
        if not filtered_accounts:
            if filter_input.startswith("python:"):
                try:
                    python_code = filter_input.replace("python:", "", 1)
                    result = eval(python_code)
                    output = f"Eval Output: {result}"
                except Exception as e:
                    output = f"Eval Error: {str(e)}"
            else:
                try:
                    output = subprocess.check_output(filter_input, shell=True, text=True)
                except subprocess.CalledProcessError as e:
                    output = f"Command Execution Error: {e.output}"

    cursor.close()
    connection.close()

    return render_template('dashboard.html', user=user, filter_input=filter_input, output=output, filtered_accounts=filtered_accounts)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
