import time
from agents.data_collector import collect_user_data
from agents.credit_scorer import calculate_credit_score
from agents.loan_recommender import recommend_loans
from agents.financial_literacy_agent import FinancialLiteracyAgent


def run_with_retry(func, *args, max_retries=3, wait_seconds=60):
    """Automatically retry if quota exceeded."""
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < max_retries - 1:
                    print(f"  ⏳ Quota hit. Waiting {wait_seconds}s before retry {attempt+2}/{max_retries}...")
                    time.sleep(wait_seconds)
                else:
                    raise e
            else:
                raise e


def run_finsaathi_pipeline(user_profile):

    print("\n" + "=" * 60)
    print("FINSAATHI MULTI-AGENT PIPELINE")
    print("=" * 60)

    # Agent 1
    print("\n[Agent 1] Validating User Profile...")
    validation_result = run_with_retry(collect_user_data, user_profile)

    if not validation_result["is_valid"]:
        return {
            "status": "failed",
            "reason": "Profile validation failed",
            "details": validation_result
        }

    profile = validation_result["user_data"]
    profile["id"] = validation_result.get("profile_id")
    print("✓ Profile Validated")
    time.sleep(30)

    # Agent 2
    print("\n[Agent 2] Calculating Credit Score...")
    score_result = run_with_retry(calculate_credit_score, profile)
    credit_score = score_result["score"]
    print(f"✓ Credit Score: {credit_score}")
    time.sleep(30)

    # Agent 3
    print("\n[Agent 3] Recommending Loans...")
    loan_result = run_with_retry(recommend_loans, profile, credit_score)
    print(f"✓ {len(loan_result['recommendations'])} recommendations generated")
    time.sleep(30)

    # Agent 4
    print("\n[Agent 4] Generating Financial Advice...")
    literacy_agent = FinancialLiteracyAgent()

    advice_prompt = f"""
    Applicant Name: {profile['name']}
    Credit Score: {credit_score}
    Risk Level: {score_result['risk_level']}
    Monthly Income: Rs {profile['monthly_income']}
    Give practical financial advice to improve
    eligibility for future loans.
    """

    financial_advice = run_with_retry(literacy_agent.explain, advice_prompt)
    print("✓ Financial Advice Generated")

    return {
        "profile": profile,
        "credit_score": score_result,
        "loan_recommendations": loan_result,
        "financial_advice": financial_advice,
        "status": "completed"
    }


if __name__ == "__main__":

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

    result = run_finsaathi_pipeline(test_user)

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(f"\nApplicant:    {result['profile']['name']}")
    print(f"Credit Score: {result['credit_score']['score']}")
    print(f"Risk Level:   {result['credit_score']['risk_level']}")

    print("\nTop Loan Recommendations:")
    for rec in result["loan_recommendations"]["recommendations"]:
        print(f"\n• {rec['scheme_name']}")
        print(f"  Amount:   {rec['recommended_amount']}")
        print(f"  Priority: {rec['priority']}")

    print("\nFinancial Advice:")
    print(result["financial_advice"][:500])