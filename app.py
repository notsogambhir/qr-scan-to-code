from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, MetaData, Table, Column, String, select
import os

app = Flask(__name__)

# Use environment variable set on Railway for DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup database connection
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the 'codes' table (your actual table)
codes = Table(
    'codes', metadata,
    Column('token_id', String, primary_key=True),
    Column('code', String),
    Column('phone_number', String),
    Column('name', String),
)

# Make sure metadata is loaded
metadata.create_all(engine)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_code = None
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']

        with engine.connect() as conn:
            # Find the next unused code
            stmt = select(codes).where(codes.c.name == None).limit(1)
            result = conn.execute(stmt).first()

            if result:
                # Update the entry with user data
                update_stmt = codes.update().where(codes.c.token_id == result.token_id).values(
                    name=name,
                    phone_number=phone_number
                )
                conn.execute(update_stmt)
                user_code = result.code
            else:
                user_code = "No available codes left."

    return render_template('index.html', user_code=user_code)

if __name__ == '__main__':
    app.run(debug=True)
