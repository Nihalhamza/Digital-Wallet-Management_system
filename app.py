from flask import Flask, render_template, request, session, redirect
from database import get_connection
from flask import flash
from decimal import Decimal
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "static/profile_pics"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "wallet_secret_key"


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]

        if not name.strip():
            flash("Name cannot be empty.", "error")
            return redirect("/register")
        if not phone.isdigit():
            flash("Phone number must contain only digits.", "error")
            return redirect("/register")

        if len(phone) != 10:
            flash("Phone number must be 10 digits.", "error")
            return redirect("/register")

        db = get_connection()
        cursor = db.cursor()

        # Check if email already exists
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            db.close()

            flash("Email already exists.", "error")
            return redirect("/register")

        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email, password, phone) VALUES (%s, %s, %s, %s)",
            (name, email, password, phone)
        )

        # Get the new user's ID
        user_id = cursor.lastrowid

        # Create wallet with ₹0 balance
        cursor.execute(
            "INSERT INTO wallet (user_id, balance) VALUES (%s, %s)",
            (user_id, 0)
        )

        db.commit()

        cursor.close()
        db.close()

        flash("Registration successful! Please login.", "success")
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:

            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            return redirect("/dashboard")

        else:

            flash("Invalid email or password.", "error")
            return redirect("/login")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT balance FROM wallet WHERE user_id=%s",
        (session["user_id"],)
    )

    wallet = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        balance=wallet["balance"]
    )


# ---------------- ADD MONEY ----------------

@app.route("/add_money", methods=["GET", "POST"])
def add_money():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        amount = Decimal(request.form["amount"])
        if amount <= 0:
            flash("Please enter an amount greater than 0.", "error")
            return redirect("/add_money")

        db = get_connection()
        cursor = db.cursor(dictionary=True)

        # Get current balance
        cursor.execute(
            "SELECT balance FROM wallet WHERE user_id=%s",
            (session["user_id"],)
        )

        wallet = cursor.fetchone()

        new_balance = wallet["balance"] + amount

        # Update wallet
        cursor.execute(
            "UPDATE wallet SET balance=%s WHERE user_id=%s",
            (new_balance, session["user_id"])
        )

        # Save transaction
        cursor.execute(
            """
            INSERT INTO transactions
            (user_id, sender_id, receiver_id,
             transaction_type, amount, status)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                None,
                None,
                "Deposit",
                amount,
                "Completed"
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/dashboard")

    return render_template("add_money.html")

# ---------------- TRANSFER MONEY ----------------

@app.route("/transfer", methods=["GET", "POST"])
def transfer():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        receiver_email = request.form["receiver_email"]
        amount = Decimal(request.form["amount"])
        if amount <= 0:
            flash("Please enter an amount greater than 0.", "error")
            return redirect("/transfer")

        db = get_connection()
        cursor = db.cursor(dictionary=True)

        # Get sender details
        cursor.execute(
            "SELECT * FROM users WHERE user_id=%s",
            (session["user_id"],)
        )
        sender = cursor.fetchone()

        if sender["email"] == receiver_email:

            flash("You cannot transfer money to yourself.", "error")
            return redirect("/transfer")

        # Find receiver
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (receiver_email,)
        )
        receiver = cursor.fetchone()

        if receiver is None:

            flash("Receiver not found.", "error")
            return redirect("/transfer")

        # Get sender wallet
        cursor.execute(
            "SELECT * FROM wallet WHERE user_id=%s",
            (session["user_id"],)
        )
        sender_wallet = cursor.fetchone()

        if sender_wallet["balance"] < amount:

            flash("Insufficient wallet balance.", "error")
            return redirect("/transfer")

        # Get receiver wallet
        cursor.execute(
            "SELECT * FROM wallet WHERE user_id=%s",
            (receiver["user_id"],)
        )
        receiver_wallet = cursor.fetchone()

        sender_new_balance = sender_wallet["balance"] - amount
        receiver_new_balance = receiver_wallet["balance"] + amount

        # Update sender wallet
        cursor.execute(
            "UPDATE wallet SET balance=%s WHERE user_id=%s",
            (sender_new_balance, session["user_id"])
        )

        # Update receiver wallet
        cursor.execute(
            "UPDATE wallet SET balance=%s WHERE user_id=%s",
            (receiver_new_balance, receiver["user_id"])
        )

        # Save transaction
        cursor.execute(
            """
            INSERT INTO transactions
            (user_id, sender_id, receiver_id,
             transaction_type, amount, status)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                session["user_id"],
                receiver["user_id"],
                "Transfer",
                amount,
                "Completed"
            )
        )

        db.commit()

        cursor.close()
        db.close()

        flash("Money transferred successfully!", "success")
        return redirect("/dashboard")

    return render_template("transfer.html")

# ---------------- TRANSACTION HISTORY ----------------

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.transaction_date,
            t.transaction_type,
            t.amount,
            t.status,
            u.email AS receiver_email
        FROM transactions t
        LEFT JOIN users u
            ON t.receiver_id = u.user_id
        WHERE t.user_id = %s
        ORDER BY t.transaction_date DESC
    """, (session["user_id"],))

    transactions = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "history.html",
        transactions=transactions
    )


# ---------------- PROFILE ----------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        profile_image = request.files.get("profile_image")

        filename = None

        # Save uploaded profile image
        if profile_image and profile_image.filename != "":

            filename = secure_filename(profile_image.filename)

            profile_image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        # Name validation
        if not name.strip():

            flash("Name cannot be empty.", "error")
            return redirect("/profile")

        # Phone validation
        if not phone.isdigit():

            flash("Phone number must contain only digits.", "error")
            return redirect("/profile")

        if len(phone) != 10:

            flash("Phone number must be 10 digits.", "error")
            return redirect("/profile")

        # Check if another user already has this email
        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            AND user_id!=%s
            """,
            (
                email,
                session["user_id"]
            )
        )

        existing_user = cursor.fetchone()

        if existing_user:

            flash("Email already exists.", "error")

            cursor.close()
            db.close()

            return redirect("/profile")

        # Update profile with image
        if filename:

            cursor.execute(
                """
                UPDATE users
                SET name=%s,
                    email=%s,
                    phone=%s,
                    profile_pic=%s
                WHERE user_id=%s
                """,
                (
                    name,
                    email,
                    phone,
                    filename,
                    session["user_id"]
                )
            )

        else:

            cursor.execute(
                """
                UPDATE users
                SET name=%s,
                    email=%s,
                    phone=%s
                WHERE user_id=%s
                """,
                (
                    name,
                    email,
                    phone,
                    session["user_id"]
                )
            )

        db.commit()

        # Keep session email updated
        session["email"] = email

        flash("Profile updated successfully.", "success")

    # Load current user
    cursor.execute(
        "SELECT * FROM users WHERE user_id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "profile.html",
        user=user
    )

# ---------------- CHANGE PASSWORD ----------------

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect("/login")

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        cursor.execute(
            "SELECT password FROM users WHERE user_id=%s",
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if user["password"] != current_password:

            cursor.close()
            db.close()

            flash("Current password is incorrect.", "error")
            return redirect("/change_password")

        if new_password != confirm_password:

            cursor.close()
            db.close()

            flash("New password won't match.", "error")
            return redirect("/change_password")

        cursor.execute(
            """
            UPDATE users
            SET password=%s
            WHERE user_id=%s
            """,
            (
                new_password,
                session["user_id"]
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/dashboard")

    cursor.close()
    db.close()

    return render_template("change_password.html")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)