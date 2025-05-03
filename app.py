from flask import Flask, request, render_template
import psycopg2
import os

app = Flask(__name__)

# DB connection
def get_db_connection():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ.get('DB_PORT', 5432)
    )

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    name = ""
    phone = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not phone or not phone.isdigit() or len(phone) != 10:
            message = "Enter a valid 10-digit phone number and name."
            return render_template("form.html", message=message, name=name, phone=phone)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT code FROM codes WHERE phone_number = %s", (phone,))
        result = cur.fetchone()

        if result:
            code = result[0]
        else:
            # Get first unassigned code
            cur.execute("SELECT token_id, code FROM codes WHERE phone_number IS NULL LIMIT 1")
            token = cur.fetchone()
            if token:
                token_id, code = token
                cur.execute("UPDATE codes SET phone_number=%s, name=%s WHERE token_id=%s", (phone, name, token_id))
                conn.commit()
            else:
                code = "No codes available."

        cur.close()
        conn.close()

        return render_template("form.html", code=code, name=name, phone=phone)

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
