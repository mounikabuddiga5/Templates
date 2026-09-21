
from flask import Flask, request, redirect, render_template, send_from_directory,session
import sqlite3
import os

# =========================================================
# FLASK SETUP
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")
DATABASE = os.path.join(BASE_DIR, "users.db")

app = Flask(
    __name__,
    template_folder=TEMPLATE_FOLDER
)
app.secret_key = "employee-management-secret-key"


# =========================================================
# STATIC FILES
# =========================================================

@app.route("/static/<path:filename>")
def static_files(filename):

    return send_from_directory(BASE_DIR, filename)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE DATABASE AND TABLES
# =========================================================

def create_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # EMPLOYEES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL,
            joining_date TEXT NOT NULL,
            address TEXT
        )
    """)

    connection.commit()

    connection.close()

    print("Database created successfully.")
    print("Database location:", DATABASE)


# =========================================================
# FIRST PAGE
# =========================================================

@app.route("/")
def welcome():

    return render_template("welcome.html")


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/home")
def home_page():

    return render_template("home.html")


# =========================================================
# REGISTER PAGE
# =========================================================

@app.route("/register")
def register_page():

    return render_template("register2.html")


# =========================================================
# REGISTER USER
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    fullname = request.form.get("fullname")
    username = request.form.get("username")
    password = request.form.get("password")

    # -----------------------------------------------------
    # CHECK EMPTY FIELDS
    # -----------------------------------------------------

    if not fullname or not username or not password:

        return """
        <h2>Please fill all fields.</h2>

        <br>

        <a href="/register">
            Go Back
        </a>
        """

    connection = get_db_connection()

    try:

        connection.execute("""
            INSERT INTO users
            (
                fullname,
                username,
                password
            )
            VALUES (?, ?, ?)
        """, (
            fullname,
            username,
            password
        ))

        connection.commit()

    except sqlite3.IntegrityError:

        connection.close()

        return """
        <h2>Username already exists!</h2>

        <br>

        <a href="/register">
            Try Again
        </a>
        """

    connection.close()

    # After registration go to login page
    return redirect("/login")


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login")
def login_page():

    return render_template("login.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    connection = get_db_connection()

    user = connection.execute("""
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?
    """, (
        username,
        password
    )).fetchone()

    connection.close()

    # -----------------------------------------------------
    # LOGIN SUCCESS
    # -----------------------------------------------------

    if user:

        return redirect("/home")

    # -----------------------------------------------------
    # LOGIN FAILED
    # -----------------------------------------------------

    else:

        return """
        <h2>Login failed!</h2>

        <p>Username or password is incorrect.</p>

        <br>

        <a href="/login">
            Try Again
        </a>
        """
    # =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# ADD EMPLOYEE PAGE
# =========================================================

@app.route("/add-employee")
def add_employee_page():

    return render_template("add-employee.html")


# =========================================================
# ADD EMPLOYEE TO DATABASE
# =========================================================

@app.route("/add-employee", methods=["POST"])
def add_employee():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    department = request.form.get("department")
    salary = request.form.get("salary")
    joining_date = request.form.get("joining_date")
    address = request.form.get("address", "")

    # -----------------------------------------------------
    # CHECK REQUIRED FIELDS
    # -----------------------------------------------------

    if (
        not name
        or not email
        or not phone
        or not department
        or not salary
        or not joining_date
    ):

        return """
        <h2>Please fill all required fields.</h2>

        <br>

        <a href="/add-employee">
            Go Back
        </a>
        """

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO employees
        (
            name,
            email,
            phone,
            department,
            salary,
            joining_date,
            address
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        phone,
        department,
        salary,
        joining_date,
        address
    ))

    connection.commit()

    connection.close()

    print("Employee added:", name)

    return redirect("/employees")


# =========================================================
# EMPLOYEES PAGE
# =========================================================

@app.route("/employees")
def employees():

    search = request.args.get("search")

    connection = get_db_connection()

    # -----------------------------------------------------
    # SEARCH EMPLOYEE
    # -----------------------------------------------------

    if search:

        employee_list = connection.execute("""
            SELECT *
            FROM employees
            WHERE name LIKE ?
            OR email LIKE ?
            OR phone LIKE ?
            OR department LIKE ?
            ORDER BY id ASC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    # -----------------------------------------------------
    # SHOW ALL EMPLOYEES
    # -----------------------------------------------------

    else:

        employee_list = connection.execute("""
            SELECT *
            FROM employees
            ORDER BY id ASC
        """).fetchall()

    connection.close()

    return render_template(
        "employee.html",
        employees=employee_list
    )


# =========================================================
# EDIT EMPLOYEE PAGE
# =========================================================

@app.route("/edit-employee/<int:id>")
def edit_employee_page(id):

    connection = get_db_connection()

    employee = connection.execute("""
        SELECT *
        FROM employees
        WHERE id = ?
    """, (id,)).fetchone()

    connection.close()

    # -----------------------------------------------------
    # EMPLOYEE NOT FOUND
    # -----------------------------------------------------

    if employee is None:

        return """
        <h2>Employee not found!</h2>

        <br>

        <a href="/employees">
            Back to Employees
        </a>
        """

    return render_template(
        "edit-employee.html",
        employee=employee
    )


# =========================================================
# UPDATE EMPLOYEE
# =========================================================

@app.route("/edit-employee/<int:id>", methods=["POST"])
def update_employee(id):

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    department = request.form.get("department")
    salary = request.form.get("salary")
    joining_date = request.form.get("joining_date")
    address = request.form.get("address", "")

    # -----------------------------------------------------
    # CHECK REQUIRED FIELDS
    # -----------------------------------------------------

    if (
        not name
        or not email
        or not phone
        or not department
        or not salary
        or not joining_date
    ):

        return f"""
        <h2>Please fill all required fields.</h2>

        <br>

        <a href="/edit-employee/{id}">
            Go Back
        </a>
        """

    connection = get_db_connection()

    connection.execute("""
        UPDATE employees
        SET
            name = ?,
            email = ?,
            phone = ?,
            department = ?,
            salary = ?,
            joining_date = ?,
            address = ?
        WHERE id = ?
    """, (
        name,
        email,
        phone,
        department,
        salary,
        joining_date,
        address,
        id
    ))

    connection.commit()

    connection.close()

    print("Employee updated:", id)

    return redirect("/employees")


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.route("/delete-employee/<int:id>")
def delete_employee(id):

    connection = get_db_connection()

    # -----------------------------------------------------
    # DELETE SELECTED EMPLOYEE
    # -----------------------------------------------------

    connection.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (id,))

    connection.commit()

    # -----------------------------------------------------
    # GET REMAINING EMPLOYEES
    # -----------------------------------------------------

    employees = connection.execute("""
        SELECT id
        FROM employees
        ORDER BY id ASC
    """).fetchall()

    # -----------------------------------------------------
    # TEMPORARILY CHANGE IDs TO NEGATIVE
    # -----------------------------------------------------

    for employee in employees:

        old_id = employee["id"]

        connection.execute("""
            UPDATE employees
            SET id = ?
            WHERE id = ?
        """, (
            -old_id,
            old_id
        ))

    connection.commit()

    # -----------------------------------------------------
    # GET EMPLOYEES AGAIN
    # -----------------------------------------------------

    employees = connection.execute("""
        SELECT id
        FROM employees
        ORDER BY id DESC
    """).fetchall()

    # -----------------------------------------------------
    # ASSIGN CONTINUOUS IDs
    # -----------------------------------------------------

    for index, employee in enumerate(employees, start=1):

        connection.execute("""
            UPDATE employees
            SET id = ?
            WHERE id = ?
        """, (
            index,
            employee["id"]
        ))

    connection.commit()

    # -----------------------------------------------------
    # RESET AUTOINCREMENT
    # -----------------------------------------------------

    max_id = connection.execute("""
        SELECT MAX(id)
        FROM employees
    """).fetchone()[0]

    if max_id is None:

        max_id = 0

    connection.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'employees'
    """)

    connection.execute("""
        INSERT INTO sqlite_sequence
        (
            name,
            seq
        )
        VALUES
        (
            'employees',
            ?
        )
    """, (max_id,))

    connection.commit()

    connection.close()

    print("Employee deleted:", id)

    return redirect("/employees")


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    create_database()
    app.run(debug=True)