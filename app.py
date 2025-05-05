from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.route("/", methods=["GET", "POST"])
def index():
    name = ""
    phone_number = ""
    code = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone_number = request.form.get("phone", "").strip()

        if not (phone_number.isdigit() and len(phone_number) == 10):
            error = "Please enter a valid 10-digit phone number."
        else:
            with engine.connect() as conn:
                # Check if phone number already exists
                result = conn.execute(text("SELECT code FROM codes WHERE phone_number = :phone"), {"phone": phone_number}).fetchone()

                if result:
                    code = result[0]
                else:
                    # Find next available token without a phone number
                    available = conn.execute(text("SELECT token_id, code FROM codes WHERE phone_number IS NULL ORDER BY token_id LIMIT 1")).fetchone()
                    if available:
                        token_id, code = available
                        conn.execute(text("UPDATE codes SET phone_number = :phone, name = :name WHERE token_id = :token_id"),
                                     {"phone": phone_number, "name": name, "token_id": token_id})
                        conn.commit()
                    else:
                        error = "No more codes available."

    return render_template("index.html", name=name, phone=phone_number, code=code, error=error)

if __name__ == "__main__":
    app.run(debug=True)

