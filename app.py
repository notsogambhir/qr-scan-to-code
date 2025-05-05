from flask import Flask, render_template, request
from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy.exc import NoResultFound
import os

app = Flask(__name__)

# Database setup using environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
tokens = metadata.tables['tokens']  # Ensure your table is named 'tokens'

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    code = None
    name = ''
    phone = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        if not phone.isdigit() or len(phone) != 10:
            message = "Phone number must be a 10-digit number."
            return render_template('index.html', message=message, code=None, name=name, phone=phone)

        with engine.begin() as conn:
            # Check if phone already exists
            result = conn.execute(select(tokens).where(tokens.c.phone_number == phone)).fetchone()
            if result:
                code = result.code
                message = "Welcome back!"
            else:
                # Assign next unused code
                new_code = conn.execute(select(tokens).where(tokens.c.phone_number == None).limit(1)).fetchone()
                if new_code:
                    conn.execute(
                        update(tokens)
                        .where(tokens.c.token_id == new_code.token_id)
                        .values(phone_number=phone, name=name)
                    )
                    code = new_code.code
                    message = "Code assigned successfully."
                else:
                    message = "No more codes available."

    return render_template('index.html', message=message, code=code, name=name, phone=phone)

if __name__ == '__main__':
    app.run(debug=True)
