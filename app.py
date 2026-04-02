from flask import Flask, request
import sqlite3
import os
app = Flask(__name__)

# 🔹 Establishing connection to SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# 🔹 Creating users table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

# 🔴 Insert users ONLY if not already present (prevents duplicates)
users = [
    ('ramya', '1234'),
    ('vardhan', 'admin123'),
    ('venu', '1529'),
    ('sudwin', '1234')
]

for user, pwd in users:
    cursor.execute("SELECT * FROM users WHERE username=?", (user,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (user, pwd))

conn.commit()


# 🔹 Login page (Frontend UI)
@app.route('/')
def login():
    return '''
    <html>
    <head>
        <title>Secure Login System</title>
        <style>
            body {
                font-family: Arial;
                background: linear-gradient(to right, #4facfe, #00f2fe);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .box {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                width: 320px;
            }
            input {
                width: 90%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            button {
                width: 100%;
                padding: 10px;
                background: #4facfe;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>🔐 Login Page</h2>

            <form action="/login" method="post">
                <input type="text" name="username" placeholder="Enter Username" required><br>
                <input type="text" name="password" placeholder="Enter Password" required><br>
                <button type="submit">Login</button>
            </form>

        </div>
    </body>
    </html>
    '''


# 🔴 Vulnerable login
@app.route('/login', methods=['POST'])
def check_login():
    username = request.form['username']
    password = request.form['password']

    # ❌ Vulnerable SQL Query (kept as it is for demonstration)
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = cursor.execute(query).fetchall()

    #to show details of the users
    # if result:
    #     output = ""
    #     for row in result:
    #         output += f"{row[1]} - {row[2]}<br>"
    #     return output
    # else:
    #     return "Login Failed"

    if result:
        return '''
        <script>
            alert("Login Successful");
            window.location.href = "https://anits.org/department/cse";
        </script>
        '''
    else:
        return "<h2 style='color:red;text-align:center;'>❌ Login Failed</h2>"


# 🔹 Running the Flask application
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
