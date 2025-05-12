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
    code = None

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone_number"]

        with engine.begin() as conn:
            # Check if this phone number already received a code
            existing = conn.execute(
                select(codes.c.code).where(codes.c.phone_number == phone)
            ).fetchone()

            if existing:
                code = existing[0]
            else:
                # Fetch the next available code
                next_token = conn.execute(
                    select(codes).where(codes.c.phone_number == None).limit(1)
                ).mappings().first()

                if next_token:
                    conn.execute(
                        update(codes)
                        .where(codes.c.token_id == next_token["token_id"])
                        .values(phone_number=phone, name=name)
                    )
                    code = next_token["code"]
                else:
                    code = "No codes available"

    return render_template("index.html", code=code)

if __name__ == "__main__":
    app.run(debug=True)
