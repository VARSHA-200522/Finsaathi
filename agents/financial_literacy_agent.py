import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from config import GOOGLE_API_KEY, MODEL_NAME

class FinancialLiteracyAgent:

    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model = MODEL_NAME

    def explain(self, question: str) -> str:
        prompt = f"""
        You are a financial literacy assistant helping
        rural Indian users understand finance simply.

        Question/Profile:
        {question}

        Provide:
        IMMEDIATE STEPS (next 30 days):
        1.
        2.
        3.

        SHORT TERM GOALS (3-6 months):
        1.
        2.

        HOW TO IMPROVE CREDIT SCORE:
        1.
        2.
        3.

        GOVERNMENT SCHEMES TO EXPLORE:
        1.
        2.

        SAVINGS TIP:
        (one practical tip for rural India)

        Keep language simple and practical for rural India.
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text

    def explain_in_hindi(self, question: str) -> str:
        prompt = f"""
        Aap ek gramin vittiya salahkar hain.
        Niche diye gaye sawaal ka Hindi mein
        saral jawab dijiye.

        Sawaal: {question}

        TURANT KADAM:
        1.
        2.

        SAVING TIPS:
        1.
        2.

        SARKARI YOJANAYEN:
        1.
        2.
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text


if __name__ == "__main__":
    print("=" * 60)
    print("FinSaathi Financial Literacy Agent")
    print("Type 'exit' to quit")
    print("=" * 60)

    agent = FinancialLiteracyAgent()

    while True:
        question = input("\nAsk a financial question: ")
        if question.lower() == "exit":
            print("Goodbye!")
            break
        try:
            answer = agent.explain(question)
            print("\n===== ANSWER =====\n")
            print(answer)
        except Exception as e:
            print(f"\nError: {e}")