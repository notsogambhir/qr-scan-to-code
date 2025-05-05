from flask import Flask, render_template, request
from sqlalchemy import create_engine, MetaData, Table, select, update
import os

app = Flask(__name__)

# Get the database URL from environment or use local SQLite for development
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///local.db')

# Set up SQLAlchemy engine and reflect the schema
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine, only=['codes'])  # Limit to just 'codes' table
codes = metadata.tables['codes']

@app.route("/", methods=["GET", "POST"])
def index():
    user_code = None

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone_number"]

        # Start a transaction block to ensure writes are committed
        with engine.begin() as conn:
            # Check if phone number already has a code
            existing = conn.execute(
                select(codes.c.code).where(codes.c.phone_number == phone)
            ).fetchone()

            if existing:
                user_code = existing[0]
            else:
                # Get the next unassigned token
                next_token = conn.execute(
                    select(codes).where(codes.c.phone_number == None).limit(1)
                ).mappings().first()

                if next_token:
                    # Update the token with user details
                    result = conn.execute(
                        update(codes)
                        .where(codes.c.token_id == next_token["token_id"])
                        .values(phone_number=phone, name=name)
                    )
                    print("Updated rows:", result.rowcount)

                    user_code = next_token["code"]
                else:
                    user_code = "No codes available"

    return render_template("index.html", user_code=user_code)

if __name__ == "__main__":
    app.run(debug=True)
