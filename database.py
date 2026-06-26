import sqlite3
import os
from config import DB_PATH

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rural_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            village TEXT NOT NULL,
            state TEXT NOT NULL,
            age INTEGER,
            occupation TEXT,
            monthly_income REAL,
            land_acres REAL,
            crop_type TEXT,
            mobile_recharges_per_month INTEGER,
            years_in_village INTEGER,
            has_bank_account INTEGER,
            existing_loans REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            score INTEGER,
            risk_level TEXT,
            score_breakdown TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES rural_profiles (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            scheme_name TEXT,
            recommended_amount REAL,
            interest_rate REAL,
            repayment_months INTEGER,
            eligibility_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES rural_profiles (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def insert_sample_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM rural_profiles")
    if cursor.fetchone()[0] > 0:
        print("Sample data already exists.")
        conn.close()
        return

    sample_profiles = [
        ("Ramu Yadav", "Rampur", "Uttar Pradesh", 38, "Farmer", 8000, 2.5, "Wheat", 4, 15, 1, 0),
        ("Sunita Devi", "Koilwar", "Bihar", 32, "Small Business", 6500, 0, "None", 3, 10, 0, 5000),
        ("Gopal Krishnan", "Thanjavur", "Tamil Nadu", 45, "Farmer", 12000, 5.0, "Rice", 6, 20, 1, 10000),
        ("Meera Bai", "Barmer", "Rajasthan", 28, "Dairy Farmer", 5500, 1.0, "None", 2, 8, 0, 0),
        ("Shyam Lal", "Hardoi", "Uttar Pradesh", 52, "Farmer", 9500, 3.5, "Sugarcane", 5, 25, 1, 15000),
    ]

    cursor.executemany('''
        INSERT INTO rural_profiles
        (name, village, state, age, occupation, monthly_income,
         land_acres, crop_type, mobile_recharges_per_month,
         years_in_village, has_bank_account, existing_loans)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_profiles)

    conn.commit()
    conn.close()
    print(f"Inserted 5 sample profiles!")

if __name__ == "__main__":
    init_db()
    insert_sample_data()