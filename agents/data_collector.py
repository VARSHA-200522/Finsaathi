import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, DB_PATH

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def collect_user_data(user_input: dict) -> dict:
    """
    Agent 1: Validates and stores rural user profile data.
    Takes raw user input and returns cleaned, validated profile.
    """
    prompt = f"""
    You are a financial data validator for rural Indian users.
    Validate and clean this user data:

    Name: {user_input.get('name', '')}
    Village: {user_input.get('village', '')}
    State: {user_input.get('state', '')}
    Age: {user_input.get('age', '')}
    Occupation: {user_input.get('occupation', '')}
    Monthly Income (Rs): {user_input.get('monthly_income', '')}
    Land Owned (acres): {user_input.get('land_acres', 0)}
    Crop Type: {user_input.get('crop_type', 'None')}
    Mobile Recharges per month: {user_input.get('mobile_recharges_per_month', 0)}
    Years in Village: {user_input.get('years_in_village', '')}
    Has Bank Account: {user_input.get('has_bank_account', 0)}
    Existing Loans (Rs): {user_input.get('existing_loans', 0)}

    Check:
    1. Is the name valid?
    2. Is the age between 18 and 80?
    3. Is monthly income realistic for rural India (Rs 2000-50000)?
    4. Are all required fields present?

    Respond in exactly this format:
    VALID: yes/no
    ISSUES: list any issues or none
    SUMMARY: one line summary of this applicant
    """

    response = model.generate_content(prompt)
    validation_result = response.text.strip()

    is_valid = "valid: yes" in validation_result.lower()

    result = {
        "user_data": user_input,
        "is_valid": is_valid,
        "validation_details": validation_result,
        "status": "approved_for_scoring" if is_valid else "rejected_invalid_data"
    }

    if is_valid:
        profile_id = save_to_database(user_input)
        result["profile_id"] = profile_id
        print(f"  ✅ Profile saved with ID: {profile_id}")
    else:
        print(f"  ❌ Invalid data: {validation_result}")

    return result

def save_to_database(user_data: dict) -> int:
    """Save validated user profile to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO rural_profiles
        (name, village, state, age, occupation, monthly_income,
         land_acres, crop_type, mobile_recharges_per_month,
         years_in_village, has_bank_account, existing_loans)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_data.get('name'),
        user_data.get('village'),
        user_data.get('state'),
        user_data.get('age'),
        user_data.get('occupation'),
        user_data.get('monthly_income'),
        user_data.get('land_acres', 0),
        user_data.get('crop_type', 'None'),
        user_data.get('mobile_recharges_per_month', 0),
        user_data.get('years_in_village'),
        user_data.get('has_bank_account', 0),
        user_data.get('existing_loans', 0)
    ))

    profile_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return profile_id

def get_profile_by_id(profile_id: int) -> dict:
    """Retrieve a profile from database by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rural_profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "village": row[2],
            "state": row[3],
            "age": row[4],
            "occupation": row[5],
            "monthly_income": row[6],
            "land_acres": row[7],
            "crop_type": row[8],
            "mobile_recharges_per_month": row[9],
            "years_in_village": row[10],
            "has_bank_account": row[11],
            "existing_loans": row[12]
        }
    return None

def get_all_profiles() -> list:
    """Retrieve all profiles from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rural_profiles")
    rows = cursor.fetchall()
    conn.close()

    profiles = []
    for row in rows:
        profiles.append({
            "id": row[0],
            "name": row[1],
            "village": row[2],
            "state": row[3],
            "age": row[4],
            "occupation": row[5],
            "monthly_income": row[6]
        })
    return profiles

if __name__ == "__main__":
    print("=" * 45)
    print("  Testing Agent 1 - Data Collector")
    print("=" * 45)

    test_user = {
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

    print("\nTesting with sample rural user from Andhra Pradesh...")
    result = collect_user_data(test_user)

    print("\n--- Agent 1 Result ---")
    print(f"Valid:   {result['is_valid']}")
    print(f"Status:  {result['status']}")
    print(f"Validation:\n{result['validation_details']}")

    if result.get('profile_id'):
        print(f"\nRetrieving saved profile...")
        profile = get_profile_by_id(result['profile_id'])
        print(f"Saved: {profile['name']} from {profile['village']}, {profile['state']}")

    print("\nAll profiles in database:")
    for p in get_all_profiles():
        print(f"  ID {p['id']}: {p['name']} - {p['village']}, {p['state']}")

    print("\n" + "=" * 45)
    print("Agent 1 test complete!")
    print("=" * 45)
    