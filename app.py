from flask import Flask, render_template, request
from orchestrator import run_finsaathi_pipeline

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    user_data = {
        "name": request.form["name"],
        "village": request.form["village"],
        "state": request.form["state"],
        "age": int(request.form["age"]),
        "occupation": request.form["occupation"],
        "monthly_income": int(request.form["monthly_income"]),
        "land_acres": float(request.form["land_acres"]),
        "crop_type": request.form["crop_type"],
        "mobile_recharges_per_month": int(request.form["mobile_recharges"]),
        "years_in_village": int(request.form["years_in_village"]),
        "has_bank_account": int(request.form["has_bank_account"]),
        "existing_loans": int(request.form["existing_loans"])
    }

    try:
        result = run_finsaathi_pipeline(user_data)
        return render_template("index.html", result=result)

    except Exception as e:
        return render_template("index.html", error_message=str(e))

if __name__ == "__main__":
    app.run(debug=True)