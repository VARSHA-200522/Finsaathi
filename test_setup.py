import sys
import os

def test_imports():
    print("Testing imports...")
    try:
        import flask
        print(f"  Flask {flask.__version__} - OK")
    except ImportError:
        print("  Flask - FAILED. Run: pip install flask")
        return False
    try:
        import google.generativeai as genai
        print("  Google Generative AI - OK")
    except ImportError:
        print("  Google GenerativeAI - FAILED. Run: pip install google-generativeai")
        return False
    try:
        import dotenv
        print("  Python-dotenv - OK")
    except ImportError:
        print("  Python-dotenv - FAILED. Run: pip install python-dotenv")
        return False
    return True

def test_api_key():
    print("\nTesting API key...")
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("  API Key - NOT SET. Add your key to .env file")
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say FinSaathi setup successful in one line.")
        print("  API Key - OK")
        print(f"  Gemini says: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"  API Key - FAILED: {e}")
        return False

def test_database():
    print("\nTesting database...")
    try:
        from database import init_db, insert_sample_data
        init_db()
        insert_sample_data()
        print("  Database - OK")
        return True
    except Exception as e:
        print(f"  Database - FAILED: {e}")
        return False

def test_folders():
    print("\nTesting folder structure...")
    all_ok = True
    for folder in ["agents", "data", "templates", "static"]:
        if os.path.exists(folder):
            print(f"  /{folder} - OK")
        else:
            print(f"  /{folder} - MISSING")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("=" * 45)
    print("   FinSaathi Day 1 Setup Test")
    print("=" * 45)
    results = []
    results.append(test_folders())
    results.append(test_imports())
    results.append(test_database())
    results.append(test_api_key())
    print("\n" + "=" * 45)
    if all(results):
        print("ALL TESTS PASSED! Ready for Day 2!")
    else:
        print("Some tests failed. Fix issues above and rerun.")
    print("=" * 45)