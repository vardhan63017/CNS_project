from flask import Flask, request
from datetime import datetime
import sqlite3

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

# 🔹 NEW: Creating login_logs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    status TEXT,
    result TEXT,
    time TEXT
)
''')

# � Ensure existing login_logs table has the time column
cursor.execute("PRAGMA table_info(login_logs)")
existing_columns = [row[1] for row in cursor.fetchall()]
if 'time' not in existing_columns:
    cursor.execute("ALTER TABLE login_logs ADD COLUMN time TEXT")

# �🔴 Insert users ONLY if not already present
users = [
    ('ramya', '1234'),
    ('vardhan', 'admin123'),
    ('venu', '1529'),
    ('sudwin', '1234')
]

for user, pwd in users:
    cursor.execute("SELECT * FROM users WHERE username=?", (user,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))

conn.commit()


# 🔹 Login page
@app.route('/')
def login():
    return '''
<html>
<head>
<title>Secure Login</title>
<style>
body {
    font-family: Arial;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.box {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    width: 320px;
    text-align: center;
}
h2 {
    margin-bottom: 20px;
}
input {
    width: 90%;
    padding: 10px;
    margin: 10px 0;
    border-radius: 6px;
    border: 1px solid #ccc;
}
input:focus {
    border-color: #667eea;
    outline: none;
}
button {
    width: 100%;
    padding: 10px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
}
button:hover {
    background: #5a67d8;
}
</style>
</head>

<body>
<div class="box">
<h2>🔐 Secure Login</h2>

<form action="/login" method="post">
<input type="text" name="username" placeholder="Enter Username" required><br>
<input type="password" name="password" placeholder="Enter Password" required><br>
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

    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    print("Executed Query:", query)  # 🔍 Debug

    result = cursor.execute(query).fetchall()
    if result:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 🔹 Detect SQL Injection
        if "OR" in username.upper() or "--" in username:
            cursor.execute("INSERT INTO login_logs (username, status, result, time) VALUES (?, ?, ?, ?)",
                           (username, "SQL Injection Attack", "❌", current_time))
        else:
            cursor.execute("INSERT INTO login_logs (username, status, result, time) VALUES (?, ?, ?, ?)",
                           (username, "Normal Login", "✔", current_time))

        conn.commit()

        # 🔥 ADMIN CHECK
        if username == "vardhan":
            return '''
            <script>
                alert("Admin Login Successful");
                window.location.href = "/logs";
            </script>
            '''
        else:
            return '''
            <script>
                alert("Login Successful");
                window.location.href = "https://anits.org/department/cse";
            </script>
            '''
    else:
        return '''
        <script>
            alert("Invalid credentials");
            window.location.href = "/";
        </script>
        '''


# 🔹 Show logs table
@app.route('/logs')
def logs():
    rows = cursor.execute("SELECT * FROM login_logs").fetchall()

    output = '''
<html>
<head>
<title>Login Activity</title>
<style>
body {
    font-family: Arial;
    background: linear-gradient(to right, #43cea2, #185a9d);
    padding: 20px;
    color: white;
}
h2 {
    text-align: center;
}
table {
    margin: auto;
    border-collapse: collapse;
    width: 80%;
    background: white;
    color: black;
    border-radius: 10px;
    overflow: hidden;
}
th {
    background: #185a9d;
    color: white;
    padding: 12px;
}
td {
    padding: 10px;
    text-align: center;
}
tr:nth-child(even) {
    background: #f2f2f2;
}
tr:hover {
    background: #ddd;
}
</style>
</head>

<body>

<h2>📊 Login Activity Dashboard</h2>

<table>
<tr><th>Username</th><th>Status</th><th>Result</th><th>Time</th></tr>
'''

    for row in rows:
        output += f"<tr><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"

    output += "</table>"
    return output


if __name__ == '__main__':
    app.run(debug=True)