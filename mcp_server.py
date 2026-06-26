# mcp_server.py
# FinSaathi MCP Server - Connects all agents via standard protocol

import json
import time
from agents.data_collector import collect_user_data, get_profile_by_id
from agents.credit_scorer import calculate_credit_score, get_credit_score
from agents.loan_recommender import recommend_loans
from agents.financial_literacy_agent import FinancialLiteracyAgent

class FinSaathiMCPServer:
    """
    MCP Server for FinSaathi Multi-Agent System.
    Exposes agent capabilities as standardized tools.
    """

    def __init__(self):
        self.name = "finsaathi-mcp-server"
        self.version = "1.0.0"
        self.literacy_agent = FinancialLiteracyAgent()
        self.tools = self._register_tools()
        print(f"✅ FinSaathi MCP Server v{self.version} initialized")
        print(f"✅ {len(self.tools)} tools registered")

    def _register_tools(self) -> dict:
        """Register all available agent tools."""
        return {
            "validate_profile": {
                "name": "validate_profile",
                "description": "Validates and stores rural user profile data",
                "agent": "Agent 1 - Data Collector",
                "input_schema": {
                    "name": "string",
                    "village": "string",
                    "state": "string",
                    "age": "integer",
                    "occupation": "string",
                    "monthly_income": "number",
                    "land_acres": "number",
                    "crop_type": "string",
                    "mobile_recharges_per_month": "integer",
                    "years_in_village": "integer",
                    "has_bank_account": "integer",
                    "existing_loans": "number"
                }
            },
            "calculate_credit_score": {
                "name": "calculate_credit_score",
                "description": "Calculates alternative credit score for rural Indians",
                "agent": "Agent 2 - Credit Scorer",
                "input_schema": {
                    "profile_id": "integer"
                }
            },
            "recommend_loans": {
                "name": "recommend_loans",
                "description": "Recommends government loan schemes based on credit score",
                "agent": "Agent 3 - Loan Recommender",
                "input_schema": {
                    "profile_id": "integer",
                    "credit_score": "integer"
                }
            },
            "get_financial_advice": {
                "name": "get_financial_advice",
                "description": "Provides personalized financial literacy advice in Hindi/English",
                "agent": "Agent 4 - Financial Literacy",
                "input_schema": {
                    "name": "string",
                    "credit_score": "integer",
                    "risk_level": "string",
                    "monthly_income": "number",
                    "language": "string"
                }
            },
            "run_full_pipeline": {
                "name": "run_full_pipeline",
                "description": "Runs complete FinSaathi pipeline through all 4 agents",
                "agent": "Orchestrator",
                "input_schema": {
                    "user_profile": "object"
                }
            }
        }

    def call_tool(self, tool_name: str, params: dict) -> dict:
        """Execute a tool by name with given parameters."""
        print(f"\n[MCP] Calling tool: {tool_name}")

        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }

        try:
            if tool_name == "validate_profile":
                return self._validate_profile(params)
            elif tool_name == "calculate_credit_score":
                return self._calculate_credit_score(params)
            elif tool_name == "recommend_loans":
                return self._recommend_loans(params)
            elif tool_name == "get_financial_advice":
                return self._get_financial_advice(params)
            elif tool_name == "run_full_pipeline":
                return self._run_full_pipeline(params)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

    def _validate_profile(self, params: dict) -> dict:
        result = collect_user_data(params)
        return {
            "success": True,
            "tool": "validate_profile",
            "agent": "Agent 1",
            "result": result
        }

    def _calculate_credit_score(self, params: dict) -> dict:
        profile_id = params.get("profile_id")
        profile = get_profile_by_id(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}
        time.sleep(30)
        result = calculate_credit_score(profile)
        return {
            "success": True,
            "tool": "calculate_credit_score",
            "agent": "Agent 2",
            "result": result
        }

    def _recommend_loans(self, params: dict) -> dict:
        profile_id = params.get("profile_id")
        credit_score = params.get("credit_score")
        profile = get_profile_by_id(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}
        time.sleep(30)
        result = recommend_loans(profile, credit_score)
        return {
            "success": True,
            "tool": "recommend_loans",
            "agent": "Agent 3",
            "result": result
        }

    def _get_financial_advice(self, params: dict) -> dict:
        language = params.get("language", "en")
        prompt = f"""
        Applicant Name: {params.get('name')}
        Credit Score: {params.get('credit_score')}
        Risk Level: {params.get('risk_level')}
        Monthly Income: Rs {params.get('monthly_income')}
        Give practical financial advice.
        """
        time.sleep(30)
        if language == "hi":
            advice = self.literacy_agent.explain_in_hindi(prompt)
        else:
            advice = self.literacy_agent.explain(prompt)
        return {
            "success": True,
            "tool": "get_financial_advice",
            "agent": "Agent 4",
            "result": {"advice": advice, "language": language}
        }

    def _run_full_pipeline(self, params: dict) -> dict:
        from orchestrator import run_finsaathi_pipeline
        result = run_finsaathi_pipeline(params.get("user_profile"))
        return {
            "success": True,
            "tool": "run_full_pipeline",
            "agent": "Orchestrator",
            "result": result
        }

    def list_tools(self) -> dict:
        """List all available MCP tools."""
        return {
            "server": self.name,
            "version": self.version,
            "total_tools": len(self.tools),
            "tools": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "agent": t["agent"]
                }
                for t in self.tools.values()
            ]
        }


if __name__ == "__main__":
    print("=" * 60)
    print("  FinSaathi MCP Server Test")
    print("=" * 60)

    server = FinSaathiMCPServer()

    print("\n--- Available Tools ---")
    tools = server.list_tools()
    for tool in tools["tools"]:
        print(f"  • {tool['name']} ({tool['agent']})")
        print(f"    {tool['description']}")

    print("\n--- Testing validate_profile tool ---")
    test_profile = {
        "name": "Ravi Kumar",
        "village": "Bellary",
        "state": "Karnataka",
        "age": 40,
        "occupation": "Farmer",
        "monthly_income": 9000,
        "land_acres": 3.0,
        "crop_type": "Maize",
        "mobile_recharges_per_month": 4,
        "years_in_village": 18,
        "has_bank_account": 1,
        "existing_loans": 8000
    }

    result = server.call_tool("validate_profile", test_profile)
    print(f"\n  Success: {result['success']}")
    print(f"  Agent:   {result['agent']}")
    if result['success']:
        print(f"  Valid:   {result['result']['is_valid']}")
        print(f"  Status:  {result['result']['status']}")

    print("\n" + "=" * 60)
    print("MCP Server test complete!")
    print("=" * 60)