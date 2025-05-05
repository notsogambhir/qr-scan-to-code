from flask import Flask, render_template, request
from sqlalchemy import create_engine, MetaData, Table, select, update, and_
import os

app = Flask(__name__)

# Use Railway's DATABASE_URL environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///local.db')  # fallback for local testing

engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Reference the table
codes = metadata.tables['codes']

@app.route("/", methods=["GET", "POST"])
def index():
    user_code = None

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone_number"]

        with engine.connect() as conn:
            # Check if phone number already has a code
            existing = conn.execute(
                select(codes.c.code).where(codes.c.phone_number == phone)
            ).fetchone()

            if existing:
                user_code = existing[0]
            else:
                # Find first row where phone_number is null
                next_token = conn.execute(
                    select(codes).where(codes.c.phone_number == None).limit(1)
                ).fetchone()

                if next_token:
                    # Assign code to new user
                    conn.execute(
                        update(codes)
                        .where(codes.c.token_id == next_token.token_id)
                        .values(phone_number=phone, name=name)
                    )
                    user_code = next_token.code
                else:
                    user_code = "No codes available"

    return render_template("index.html", user_code=user_code)

if __name__ == "__main__":
    app.run(debug=True)
