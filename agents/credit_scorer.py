import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, DB_PATH

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def calculate_credit_score(profile: dict) -> dict:
    prompt = f"""
    You are an expert rural credit analyst for India.
    Calculate an alternative credit score for this person
    who has NO traditional credit history.
    
    APPLICANT PROFILE:
    Name: {profile.get('name')}
    Age: {profile.get('age')}
    Village: {profile.get('village')}, {profile.get('state')}
    Occupation: {profile.get('occupation')}
    Monthly Income: Rs {profile.get('monthly_income')}
    Land Owned: {profile.get('land_acres')} acres
    Crop Type: {profile.get('crop_type')}
    Mobile Recharges/Month: {profile.get('mobile_recharges_per_month')}
    Years in Village: {profile.get('years_in_village')}
    Has Bank Account: {'Yes' if profile.get('has_bank_account') else 'No'}
    Existing Loans: Rs {profile.get('existing_loans')}
    
    SCORING CRITERIA:
    1. Income Stability (0-25 points)
       - Regular income > Rs 8000: 25 pts
       - Regular income Rs 5000-8000: 20 pts
       - Regular income Rs 3000-5000: 15 pts
       - Below Rs 3000: 10 pts
    2. Asset Ownership (0-25 points)
       - Land > 3 acres: 25 pts
       - Land 1-3 acres: 20 pts
       - Land < 1 acre: 10 pts
       - No land: 5 pts
    3. Community Stability (0-20 points)
       - 20+ years in village: 20 pts
       - 10-20 years: 15 pts
       - 5-10 years: 10 pts
       - Below 5 years: 5 pts
    4. Digital Footprint (0-15 points)
       - 5+ recharges/month: 15 pts
       - 3-4 recharges/month: 10 pts
       - 1-2 recharges/month: 5 pts
    5. Banking History (0-15 points)
       - Has bank account + no loans: 15 pts
       - Has bank account + some loans: 10 pts
       - No bank account: 5 pts
    
    Respond in exactly this format:
    SCORE: (number between 300-850)
    INCOME_POINTS: (0-25)
    ASSET_POINTS: (0-25)
    COMMUNITY_POINTS: (0-20)
    DIGITAL_POINTS: (0-15)
    BANKING_POINTS: (0-15)
    RISK_LEVEL: (Low/Medium/High)
    RECOMMENDATION: (one sentence)
    STRENGTHS: (two key strengths)
    WEAKNESSES: (two key weaknesses or none)
    """

    response = model.generate_content(prompt)
    raw_result = response.text.strip()

    def extract_value(text, key):
        for line in text.split('\n'):
            if line.startswith(f"{key}:"):
                return line.replace(f"{key}:", "").strip()
        return "N/A"

    score = extract_value(raw_result, "SCORE")
    risk_level = extract_value(raw_result, "RISK_LEVEL")
    recommendation = extract_value(raw_result, "RECOMMENDATION")
    strengths = extract_value(raw_result, "STRENGTHS")
    weaknesses = extract_value(raw_result, "WEAKNESSES")

    try:
        score_int = int(''.join(filter(str.isdigit, score)))
        score_int = max(300, min(850, score_int))
    except:
        score_int = 500

    save_credit_score(profile.get('id'), score_int, risk_level, raw_result)

    return {
        "profile_id": profile.get('id'),
        "name": profile.get('name'),
        "score": score_int,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "raw_breakdown": raw_result,
        "status": "scored_successfully"
    }

def save_credit_score(profile_id, score, risk_level, breakdown):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO credit_scores
        (profile_id, score, risk_level, score_breakdown)
        VALUES (?, ?, ?, ?)
    ''', (profile_id, score, risk_level, breakdown))
    conn.commit()
    conn.close()

def get_credit_score(profile_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM credit_scores
        WHERE profile_id = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (profile_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "profile_id": row[1],
            "score": row[2],
            "risk_level": row[3],
            "breakdown": row[4]
        }
    return None

if __name__ == "__main__":
    print("=" * 45)
    print("  Testing Agent 2 - Credit Scorer")
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

    print(f"\nCalculating credit score for {test_profile['name']}...")
    result = calculate_credit_score(test_profile)

    print("\n--- Agent 2 Result ---")
    print(f"Name:           {result['name']}")
    print(f"Credit Score:   {result['score']} / 850")
    print(f"Risk Level:     {result['risk_level']}")
    print(f"Strengths:      {result['strengths']}")
    print(f"Weaknesses:     {result['weaknesses']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Status:         {result['status']}")

    print("\n" + "=" * 45)
    print("Agent 2 test complete!")
    print("=" * 45)
                        