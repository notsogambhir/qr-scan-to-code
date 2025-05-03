from flask import Flask, request, render_template_string
import pandas as pd

app = Flask(__name__)
DATA_FILE = "codes.csv"

# HTML template with embedded form and result output
HTML_TEMPLATE = """
<html>
    <head>
        <title>Get Your Code</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding-top: 50px; 
                background-color: #f7f7f7;
            }}
            input {{
                padding: 10px; 
                margin: 10px; 
                width: 250px;
                font-size: 16px;
            }}
            button {{
                padding: 10px 30px; 
                font-size: 18px;
                background-color: #28a745; 
                color: white; 
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .code-box {{
                font-size: 36px; 
                color: #2c7;
                margin-top: 30px;
            }}
            .container {{
                background-color: white;
                max-width: 500px;
                margin: auto;
                padding: 30px;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Code Access</h1>
            {form}
            {result}
        </div>
    </body>
</html>
"""

# HTML form shown on GET and POST
FORM_HTML = '''
<form method="POST">
    <input type="text" name="name" placeholder="Your Name" required><br>
    <input type="text" name="phone" placeholder="Phone Number" required><br>
    <button type="submit">Get My Code</button>
</form>
'''

@app.route("/", methods=["GET", "POST"])
def home():
    df = pd.read_csv(DATA_FILE, dtype=str)  # Ensure all values are strings
    result = ""

    if request.method == "POST":
        name = request.form["name"].strip()
        raw_phone = request.form["phone"]

        # Clean and format the phone number
        phone = "".join(filter(str.isdigit, raw_phone))  # Remove non-digits

        if len(phone) != 10:
            result = "<p style='color: red;'>Please enter a valid 10-digit phone number.</p>"
            return render_template_string(HTML_TEMPLATE.format(form=FORM_HTML, result=result))

        # Normalize all phone numbers in the CSV
        df["phone_number"] = df["phone_number"].fillna("").astype(str).str.replace(r"\D", "", regex=True)

        # Check if phone number already exists
        existing = df[df["phone_number"] == phone]

        if not existing.empty:
            code = existing.iloc[0]["code"]
        else:
            available = df[df["phone_number"] == ""]
            if available.empty:
                result = "<p>No more codes available!</p>"
                return render_template_string(HTML_TEMPLATE.format(form=FORM_HTML, result=result))

            # Assign code to new user
            index = available.index[0]
            df.at[index, "phone_number"] = phone
            df.at[index, "name"] = name
            code = df.at[index, "code"]

            # Save updated data
            df.to_csv(DATA_FILE, index=False)

        result = f"<div class='code-box'>Your Code: {code}</div>"

    return render_template_string(HTML_TEMPLATE.format(form=FORM_HTML, result=result))

if __name__ == "__main__":
    app.run(debug=True)
