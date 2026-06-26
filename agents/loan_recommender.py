import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, DB_PATH

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Real Indian government schemes database
GOVERNMENT_SCHEMES = {
    "PM Mudra Yojana": {
        "min_score": 400,
        "max_loan": 1000000,
        "interest_rate": 8.5,
        "description": "Micro loans for small businesses and farmers",
        "repayment_months": 60
    },
    "Kisan Credit Card": {
        "min_score": 450,
        "max_loan": 300000,
        "interest_rate": 7.0,
        "description": "Short term credit for farmers for crop cultivation",
        "repayment_months": 12
    },
    "PM Jan Dhan Yojana Loan": {
        "min_score": 300,
        "max_loan": 10000,
        "interest_rate": 0.0,
        "description": "Zero interest overdraft for Jan Dhan account holders",
        "repayment_months": 6
    },
    "NABARD Rural Credit": {
        "min_score": 500,
        "max_loan": 500000,
        "interest_rate": 9.0,
        "description": "Agricultural development loans via NABARD",
        "repayment_months": 84
    },
    "Mahila Udyam Nidhi": {
        "min_score": 450,
        "max_loan": 1000000,
        "interest_rate": 10.0,
        "description": "Special loans for women entrepreneurs",
        "repayment_months": 120
    },
    "PM SVANidhi": {
        "min_score": 300,
        "max_loan": 50000,
        "interest_rate": 7.0,
        "description": "Street vendor loans with digital payment incentives",
        "repayment_months": 12
    },
    "Dairy Entrepreneurship Development": {
        "min_score": 400,
        "max_loan": 700000,
        "interest_rate": 6.5,
        "description": "Loans for dairy farming and cattle purchase",
        "repayment_months": 60
    }
}

def recommend_loans(profile: dict, credit_score: int) -> dict:
    """
    Agent 3: Recommends best loan schemes based on
    credit score and profile.
    """
    # Filter eligible schemes based on credit score
    eligible_schemes = {
        name: details
        for name, details in GOVERNMENT_SCHEMES.items()
        if credit_score >= details["min_score"]
    }

    prompt = f"""
    You are a rural financial advisor in India.
    Recommend the best loan schemes for this applicant.
    
    APPLICANT:
    Name: {profile.get('name')}
    Occupation: {profile.get('occupation')}
    Monthly Income: Rs {profile.get('monthly_income')}
    Land: {profile.get('land_acres')} acres
    Crop: {profile.get('crop_type')}
    Has Bank Account: {'Yes' if profile.get('has_bank_account') else 'No'}
    Existing Loans: Rs {profile.get('existing_loans')}
    Credit Score: {credit_score}/850
    Gender hint from name: analyze from name
    
    ELIGIBLE SCHEMES:
    {format_schemes(eligible_schemes)}
    
    Based on the applicant's profile and credit score,
    recommend the TOP 3 most suitable schemes.
    
    Respond in exactly this format for each scheme:
    
    SCHEME_1_NAME: (scheme name)
    SCHEME_1_AMOUNT: (recommended loan amount in Rs)
    SCHEME_1_REASON: (why this scheme fits this person)
    SCHEME_1_PRIORITY: (High/Medium/Low)
    
    SCHEME_2_NAME: (scheme name)
    SCHEME_2_AMOUNT: (recommended loan amount in Rs)
    SCHEME_2_REASON: (why this scheme fits this person)
    SCHEME_2_PRIORITY: (High/Medium/Low)
    
    SCHEME_3_NAME: (scheme name)
    SCHEME_3_AMOUNT: (recommended loan amount in Rs)
    SCHEME_3_REASON: (why this scheme fits this person)
    SCHEME_3_PRIORITY: (High/Medium/Low)
    
    OVERALL_ADVICE: (two sentences of overall financial advice)
    MAX_RECOMMENDED_LOAN: (total maximum loan amount recommended)
    """

    response = model.generate_content(prompt)
    raw_result = response.text.strip()

    def extract_value(text, key):
        for line in text.split('\n'):
            if line.strip().startswith(f"{key}:"):
                return line.replace(f"{key}:", "").strip()
        return "N/A"

    # Build recommendations list
    recommendations = []
    for i in range(1, 4):
        scheme_name = extract_value(raw_result, f"SCHEME_{i}_NAME")
        scheme_amount = extract_value(raw_result, f"SCHEME_{i}_AMOUNT")
        scheme_reason = extract_value(raw_result, f"SCHEME_{i}_REASON")
        scheme_priority = extract_value(raw_result, f"SCHEME_{i}_PRIORITY")

        if scheme_name != "N/A":
            # Get interest rate from our database
            interest_rate = 0
            repayment_months = 12
            for name, details in GOVERNMENT_SCHEMES.items():
                if name.lower() in scheme_name.lower():
                    interest_rate = details["interest_rate"]
                    repayment_months = details["repayment_months"]
                    break

            recommendations.append({
                "scheme_name": scheme_name,
                "recommended_amount": scheme_amount,
                "reason": scheme_reason,
                "priority": scheme_priority,
                "interest_rate": interest_rate,
                "repayment_months": repayment_months
            })

            # Save to database
            save_recommendation(
                profile.get('id'),
                scheme_name,
                scheme_amount,
                interest_rate,
                repayment_months,
                scheme_reason
            )

    overall_advice = extract_value(raw_result, "OVERALL_ADVICE")
    max_loan = extract_value(raw_result, "MAX_RECOMMENDED_LOAN")

    return {
        "profile_id": profile.get('id'),
        "name": profile.get('name'),
        "credit_score": credit_score,
        "eligible_schemes_count": len(eligible_schemes),
        "recommendations": recommendations,
        "overall_advice": overall_advice,
        "max_recommended_loan": max_loan,
        "status": "recommendations_generated"
    }

def format_schemes(schemes: dict) -> str:
    """Format schemes for prompt."""
    result = ""
    for name, details in schemes.items():
        result += f"""
- {name}:
  Max Loan: Rs {details['max_loan']}
  Interest Rate: {details['interest_rate']}%
  Description: {details['description']}
  Repayment: {details['repayment_months']} months
"""
    return result

def save_recommendation(profile_id, scheme_name,
                         amount, interest_rate,
                         repayment_months, reason):
    """Save loan recommendation to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        amount_clean = float(''.join(
            filter(lambda x: x.isdigit() or x == '.', str(amount))
        ))
    except:
        amount_clean = 0.0

    cursor.execute('''
        INSERT INTO loan_recommendations
        (profile_id, scheme_name, recommended_amount,
         interest_rate, repayment_months, eligibility_reason)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (profile_id, scheme_name, amount_clean,
          interest_rate, repayment_months, reason))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("=" * 45)
    print("  Testing Agent 3 - Loan Recommender")
    print("=" * 45)

    test_profile = {
        "id": 6,
        "name": "Lakshmi Devi",
        "village": "Nandyal",
        "state": "Andhra Pradesh",
        "age": 35,
        "occupation": "Farmer",
        "monthly_income": 7500,
        "land_acres": 2.0,
        "crop_type": "Cotton",
        "mobile_recharges_per_month": 3,
        "years_in_village": 12,
        "has_bank_account": 1,
        "existing_loans": 5000
    }

    credit_score = 654

    print(f"\nGenerating loan recommendations for {test_profile['name']}...")
    print(f"Credit Score: {credit_score}/850\n")

    result = recommend_loans(test_profile, credit_score)

    print("--- Agent 3 Result ---")
    print(f"Name: {result['name']}")
    print(f"Eligible Schemes: {result['eligible_schemes_count']}")
    print(f"Max Recommended Loan: {result['max_recommended_loan']}")
    print(f"\nTop Recommendations:")

    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n  {i}. {rec['scheme_name']}")
        print(f"     Amount:   Rs {rec['recommended_amount']}")
        print(f"     Interest: {rec['interest_rate']}%")
        print(f"     Priority: {rec['priority']}")
        print(f"     Reason:   {rec['reason']}")

    print(f"\nOverall Advice: {result['overall_advice']}")
    print(f"Status: {result['status']}")

    print("\n" + "=" * 45)
    print("Agent 3 test complete!")
    print("=" * 45)